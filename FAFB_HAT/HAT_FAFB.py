import flybrains
import json
import navis
import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from fafbseg import flywire
import types
import pickle as pkl
# make sure the flywire token has been save in ~/.cloudvolume/secrets/global.daf-apis.com-cave-secret.json
flywire.set_default_dataset("flat_783") 



class hat_fafb():
    """This class will create a folder with the name of the hemileage in the root path. 
    The folder will be structured as follows:
    root_path/hemileage/
        ├── hemileage_meta.csv
        ├── hemileage_meshes.pkl
        ├── hemileage_CBF_meshes.pkl
        ├── JRC2018U_hemileage_meshes.pkl
        ├── JRC2018U_hemileage_CBF_meshes.pkl
        ├── JRC2018U_hemileage_meshes.nrrd
        ├── ......
    The general naming convention is <space>_<hemileage>_<type>.<extension>
    File will only be created when they are required.

    ito_lee_hemilineage is used to search for the hemileage metadata in the flybrains database.

    """
    def __init__(self, hemileage: str, root_path: str = None):
        
        if not isinstance(hemileage, str):
            raise TypeError("hemileage must be a string")
        self.hemileage = hemileage
        # set current working directory as root path if not provided
        if root_path is None:
            self.root_path = os.getcwd()
        else:
            if not isinstance(root_path, str):
                raise TypeError("root_path must be a string")
            self.root_path = root_path

        # check if a folder with named with hemileage exists
        if not os.path.exists(os.path.join(self.root_path, self.hemileage)):
            # create the folder if it does not exist
            os.makedirs(os.path.join(self.root_path, self.hemileage))

        # check if hemileage metadata exists
        self.hemilineage_meta_file = f'{self.hemileage}_meta.csv'
        _, self.hemi_neuron_ids = self._get_hemileage_meta(self.hemilineage_meta_file)

        # # check if neuron meshes exist
        # self.neuron_meshes_file = f'{self.hemileage}_meshes.pkl'
        # if not self._file_exists(self.neuron_meshes_file):
        #     _ = self._get_hemileage_mesh(self.neuron_meshes_file, self.hemi_neuron_ids)

        
        # # other attributes
        self.CBF = False
        self.threshold = 0.1
        self.templates = []
        # self.CBF_neuron_meshes_file = None
        # self.template = None
        # self.registered_neuron_meshes_file = None
        # self.registered_CBF_neuron_meshes_file = None
        # self.neuron_meshes_nrrd_file = None
        # self.CBF_neuron_meshes_nrrd_file = None

        # # save the attributes to a json file
        self.update_attributes() 



    
    def update_attributes(self):
        """
        Save current attributes to a json file in the hemileage directory.
        """
        attributes = {
            "hemileage": self.hemileage,
            "root_path": self.root_path,
            "hemilineage_meta_file": self.hemilineage_meta_file,
            "hemi_neuron_ids": self.hemi_neuron_ids.tolist() if isinstance(self.hemi_neuron_ids, np.ndarray) else self.hemi_neuron_ids,
            "CBF": self.CBF,
            "threshold": self.threshold,
            "templates": self.templates
        }
        attributes_file = os.path.join(self.root_path, self.hemileage, f'{self.hemileage}_attributes.json')
        with open(attributes_file, 'w') as f:
            json.dump(attributes, f, indent=4)
    def _save_pkl(self, file_name: str, data):
        """
        Save data to a pickle file in the hemileage directory.
        """
        with open(os.path.join(self.root_path, self.hemileage, file_name), 'wb') as f:
            pkl.dump(data, f)
    def _load_pkl(self, file_name: str):
        """
        Load data from a pickle file in the hemileage directory.
        """
        with open(os.path.join(self.root_path, self.hemileage, file_name), 'rb') as f:
            return pkl.load(f)

    def _file_exists(self, file_name: str):
        """
        Check if a file exists in the hemileage directory.
        """
        return os.path.exists(os.path.join(self.root_path, self.hemileage, file_name))
        
    def _get_hemileage_meta(self, file_path: str):
        """
        Get hemileage metadata from the flybrains database.
        """
        if not self._file_exists(self.hemilineage_meta_file):
            # get hemileage metadata from the flybrains database
            NC = flywire.NeuronCriteria
            hemi_meta_df = flywire.search_annotations(NC(ito_lee_hemilineage=self.hemileage))
            # save the metadata to a csv file
            hemi_meta_df.to_csv(os.path.join(self.root_path, self.hemileage, self.hemilineage_meta_file), index=False)
        else:
            # load the hemileage metadata from the csv file
            hemi_meta_df = pd.read_csv(os.path.join(self.root_path, self.hemileage, self.hemilineage_meta_file))

        root_ids = hemi_meta_df['root_id'].values

        return hemi_meta_df, root_ids
    
    def _get_neuron_mesh(self,file_path):
        """
        Get the mesh of a neuron from the flywire database.
        """
        def assign_soma_pos(neuron_id):
            soma = flywire.get_somas(neuron_id)
            if soma.empty:
                return None
            return soma['pt_position'].values[0]
        neuron_id = self.hemi_neuron_ids  # assuming we want the mesh of the first neuron in the hemileage
        if not self._file_exists(file_path):
            # get the meshes of the neurons from the flybrains database
            neuron_meshes = flywire.get_mesh_neuron(neuron_id)
            neuron_meshes.set_neuron_attributes(assign_soma_pos, 'soma_pos')
            # save the meshes to a pickle file
            self._save_pkl(file_path, neuron_meshes)
        else:
            # load the neuron meshes from the pickle file
            neuron_meshes = self._load_pkl(file_path)
        return neuron_meshes
    
    def _mesh_CBF(self, file_path: str, threshold: float = 0.2, update: bool = False):

        neuron_meshes = self._get_neuron_mesh(f"{self.hemileage}_meshes.pkl")
        if self._file_exists(file_path) and not update:
            CBF_neuron_meshes = self._load_pkl(file_path)
        else:
            # get the meshes of the CBF neurons from the flybrains database
            CBF_neuron_meshes = navis.cell_body_fiber(neuron_meshes, threshold=threshold)
            # save the meshes to a pickle file
            self._save_pkl(file_path, CBF_neuron_meshes)
        self.CBF = True
        self.threshold = threshold
        return CBF_neuron_meshes
    
    def _combine_voxels(self, voxel_neuron_list):
        sample_neuron = voxel_neuron_list[0].copy()
        combined_grid = sample_neuron.grid
        for voxel_neuron in voxel_neuron_list[1:]:
            combined_grid = np.logical_or(combined_grid, voxel_neuron.grid)
        sample_neuron.grid = combined_grid
        return sample_neuron
    
    def _save_nrrd(self, file_path: str, neuron_meshes):
        bbox = np.array(flybrains.JRC2018U.boundingbox).reshape(3,2)
        voxel_neuron_list =  navis.voxelize(neuron_meshes, pitch = 0.38, bounds=bbox)
        combined_voxel_neuron = self._combine_voxels(voxel_neuron_list)
        # also save a z-projection of the voxelized neuron as a 2D png image
        z_projection = combined_voxel_neuron.grid.max(axis=2)
        plt.imshow(z_projection.T, cmap='gray')
        plt.axis('off')
        # change image orientation to match the flywire orientation
        # exchange x and y axes
        plt.savefig(os.path.join(self.root_path, self.hemileage, 
                                 file_path.replace('.nrrd', '.png')), bbox_inches='tight', 
                                 pad_inches=0)
        plt.close()
        saving_path = os.path.join(self.root_path, self.hemileage, file_path)
        navis.write_nrrd(combined_voxel_neuron, saving_path)

    def get_registered_meshes(self, file_path: str, CBF_threshold: float = 0.2, update: bool = False,
                        template: str = "JRC2018U", source: str = "FLYWIRE"):
        """
        Register the neuron meshes to a template.
        Assuming the templates have been downloaded as discribed in navis_flybrains documentation.
        """
        if not isinstance(template, str):
            raise TypeError("template must be a string")
        if template not in self.templates:
            # add the template to the list of templates
            self.templates.append(template)
        if self._file_exists(file_path) and not update:
            registered_meshes = self._load_pkl(file_path)
            return registered_meshes
        elif "CBF" in file_path:
            # get the CBF neuron meshes
            neuron_meshes = self._mesh_CBF(f"{self.hemileage}_CBF_meshes.pkl", threshold=CBF_threshold, update=update)
        else:
            # get the neuron meshes
            neuron_meshes = self._get_neuron_mesh(f"{self.hemileage}_meshes.pkl")
        registered_meshes = navis.xform_brain(neuron_meshes, source=source, target=template)
        self._save_pkl(file_path, registered_meshes)
        nrrd_file_path = file_path.replace('.pkl', '.nrrd')
        self._save_nrrd(nrrd_file_path, registered_meshes)
        self.update_attributes()
        return registered_meshes

    def register_meshes(self, CBF: bool = False, CBF_threshold: float = 0.2, update: bool = False,
                        template: str = "JRC2018U", source: str = "FLYWIRE"):
        file_path = f"{self.hemileage}_registered_meshes.pkl"
        if CBF:
            file_path = f"{self.hemileage}_CBF_registered_meshes.pkl"
        registered_meshes = self.get_registered_meshes(file_path, CBF_threshold=CBF_threshold, update=update,
                                                       template=template, source=source)
        return file_path, registered_meshes
