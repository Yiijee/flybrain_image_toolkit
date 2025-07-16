#!/usr/bin/env python3
"""
Hemilineage Batch Processor with Separate Status Tracking

This script processes hemilineages from a specified batch in the hemileage_summary.csv file.
It updates separate status columns for whole neuron and CBF processing:

Status codes:
- 0: Not started
- 1: Completed
- -1: Error

Columns:
- status_whole_neuron: Status for CBF=False processing
- status_cbf: Status for CBF=True processing

Usage:
    python process_batch_v2.py <batch_number> [options]

Example:
    python process_batch_v2.py 0 --whole_neuron --cbf --cbf_threshold 0.1
"""

import argparse
import logging
import os
import sys
import pandas as pd
import traceback
from datetime import datetime
from HAT_FAFB import hat_fafb

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hemilineage_processing.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class HemilineageBatchProcessorV2:
    """Process hemilineages from a specific batch with separate status tracking."""
    
    def __init__(self, csv_file='hemileage_summary.csv'):
        """
        Initialize the batch processor.
        
        Args:
            csv_file (str): Path to the hemileage summary CSV file
        """
        self.csv_file = csv_file
        self.df = None
        self.load_summary()
    
    def load_summary(self):
        """Load the hemileage summary from CSV file."""
        try:
            self.df = pd.read_csv(self.csv_file)
            
            # Check if required columns exist
            required_columns = ['status_whole_neuron', 'status_cbf']
            missing_columns = [col for col in required_columns if col not in self.df.columns]
            
            if missing_columns:
                logger.error(f"Missing required columns in CSV: {missing_columns}")
                logger.error("Expected columns: status_whole_neuron, status_cbf")
                sys.exit(1)
            
            logger.info(f"Loaded hemileage summary with {len(self.df)} entries")
        except FileNotFoundError:
            logger.error(f"CSV file {self.csv_file} not found")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error loading CSV file: {e}")
            sys.exit(1)
    
    def save_summary(self):
        """Save the updated hemileage summary back to CSV file."""
        try:
            # Create backup
            backup_file = f"{self.csv_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.df.to_csv(backup_file, index=False)
            logger.info(f"Created backup: {backup_file}")
            
            # Save updated file
            self.df.to_csv(self.csv_file, index=False)
            logger.info(f"Updated {self.csv_file}")
        except Exception as e:
            logger.error(f"Error saving CSV file: {e}")
    
    def get_batch_hemilineages(self, batch_number):
        """
        Get all hemilineages for a specific batch.
        
        Args:
            batch_number (int): Batch number to process
            
        Returns:
            pd.DataFrame: DataFrame containing hemilineages for the specified batch
        """
        batch_df = self.df[self.df['batches'] == batch_number].copy()
        logger.info(f"Found {len(batch_df)} hemilineages in batch {batch_number}")
        return batch_df
    
    def update_status(self, hemilineage, status_column, status):
        """
        Update the status of a specific hemilineage.
        
        Args:
            hemilineage (str): Name of the hemilineage
            status_column (str): Either 'status_whole_neuron' or 'status_cbf'
            status (int): Status code (0=not started, 1=completed, -1=error)
        """
        mask = self.df['ito_lee_hemilineage'] == hemilineage
        if mask.any():
            self.df.loc[mask, status_column] = status
            logger.info(f"Updated {hemilineage} {status_column} to {status}")
        else:
            logger.warning(f"Hemilineage {hemilineage} not found in summary")
    
    def process_hemilineage(self, hemilineage, process_whole_neuron=False, process_cbf=False,
                          cbf_threshold=0.2, template="JRC2018U", source="FLYWIRE", update=False):
        """
        Process a single hemilineage using the hat_fafb class.
        
        Args:
            hemilineage (str): Name of the hemilineage to process
            process_whole_neuron (bool): Whether to process whole neuron (CBF=False)
            process_cbf (bool): Whether to process CBF version (CBF=True)
            cbf_threshold (float): Threshold for CBF processing
            template (str): Target brain template
            source (str): Source coordinate system
            update (bool): Force update of existing files
            
        Returns:
            dict: Results of processing {'whole_neuron': bool, 'cbf': bool}
        """
        results = {'whole_neuron': None, 'cbf': None}
        
        if not (process_whole_neuron or process_cbf):
            logger.warning(f"No processing requested for {hemilineage}")
            return results
        
        try:
            logger.info(f"Starting processing of {hemilineage}")
            
            # Create hat_fafb instance
            hemi_processor = hat_fafb(hemilineage)
            
            # Process whole neuron (CBF=False)
            if process_whole_neuron:
                try:
                    logger.info(f"Processing whole neuron for {hemilineage}")
                    file_path, registered_meshes = hemi_processor.register_meshes(
                        CBF=False,
                        CBF_threshold=cbf_threshold,
                        update=update,
                        template=template,
                        source=source
                    )
                    logger.info(f"Successfully processed whole neuron for {hemilineage}, output: {file_path}")
                    self.update_status(hemilineage, 'status_whole_neuron', 1)
                    results['whole_neuron'] = True
                    
                except Exception as e:
                    logger.error(f"Error processing whole neuron for {hemilineage}: {e}")
                    self.update_status(hemilineage, 'status_whole_neuron', -1)
                    results['whole_neuron'] = False
            
            # Process CBF version (CBF=True)
            if process_cbf:
                try:
                    logger.info(f"Processing CBF for {hemilineage}")
                    file_path, registered_meshes = hemi_processor.register_meshes(
                        CBF=True,
                        CBF_threshold=cbf_threshold,
                        update=update,
                        template=template,
                        source=source
                    )
                    logger.info(f"Successfully processed CBF for {hemilineage}, output: {file_path}")
                    self.update_status(hemilineage, 'status_cbf', 1)
                    results['cbf'] = True
                    
                except Exception as e:
                    logger.error(f"Error processing CBF for {hemilineage}: {e}")
                    self.update_status(hemilineage, 'status_cbf', -1)
                    results['cbf'] = False
            
            # Save changes after each hemilineage
            self.save_summary()
            
            return results
            
        except Exception as e:
            logger.error(f"Critical error processing {hemilineage}: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Mark as error for requested processing types
            if process_whole_neuron:
                self.update_status(hemilineage, 'status_whole_neuron', -1)
            if process_cbf:
                self.update_status(hemilineage, 'status_cbf', -1)
            
            self.save_summary()
            
            return {'whole_neuron': False if process_whole_neuron else None, 
                   'cbf': False if process_cbf else None}
    
    def process_batch(self, batch_number, process_whole_neuron=False, process_cbf=False,
                     cbf_threshold=0.2, template="JRC2018U", source="FLYWIRE", update=False,
                     skip_completed=True):
        """
        Process all hemilineages in a specific batch.
        
        Args:
            batch_number (int): Batch number to process
            process_whole_neuron (bool): Whether to process whole neuron (CBF=False)
            process_cbf (bool): Whether to process CBF version (CBF=True)
            cbf_threshold (float): Threshold for CBF processing
            template (str): Target brain template
            source (str): Source coordinate system
            update (bool): Force update of existing files
            skip_completed (bool): Skip hemilineages with status 1 (completed)
            
        Returns:
            dict: Summary of processing results
        """
        batch_df = self.get_batch_hemilineages(batch_number)
        
        if len(batch_df) == 0:
            logger.warning(f"No hemilineages found for batch {batch_number}")
            return {'total': 0, 'whole_neuron': {'successful': 0, 'failed': 0, 'skipped': 0}, 
                   'cbf': {'successful': 0, 'failed': 0, 'skipped': 0}}
        
        results = {
            'total': len(batch_df),
            'whole_neuron': {'successful': 0, 'failed': 0, 'skipped': 0},
            'cbf': {'successful': 0, 'failed': 0, 'skipped': 0}
        }
        
        for _, row in batch_df.iterrows():
            hemilineage = row['ito_lee_hemilineage']
            whole_neuron_status = row['status_whole_neuron']
            cbf_status = row['status_cbf']
            
            # Determine what to process
            process_wn = process_whole_neuron and (not skip_completed or whole_neuron_status != 1)
            process_cb = process_cbf and (not skip_completed or cbf_status != 1)
            
            # Skip logging for completed items
            if skip_completed:
                if process_whole_neuron and whole_neuron_status == 1:
                    logger.info(f"Skipping whole neuron for {hemilineage} (already completed)")
                    results['whole_neuron']['skipped'] += 1
                    process_wn = False
                
                if process_cbf and cbf_status == 1:
                    logger.info(f"Skipping CBF for {hemilineage} (already completed)")
                    results['cbf']['skipped'] += 1
                    process_cb = False
            
            if not (process_wn or process_cb):
                continue
            
            # Process the hemilineage
            hemi_results = self.process_hemilineage(
                hemilineage=hemilineage,
                process_whole_neuron=process_wn,
                process_cbf=process_cb,
                cbf_threshold=cbf_threshold,
                template=template,
                source=source,
                update=update
            )
            
            # Update results
            if hemi_results['whole_neuron'] is True:
                results['whole_neuron']['successful'] += 1
            elif hemi_results['whole_neuron'] is False:
                results['whole_neuron']['failed'] += 1
            
            if hemi_results['cbf'] is True:
                results['cbf']['successful'] += 1
            elif hemi_results['cbf'] is False:
                results['cbf']['failed'] += 1
        
        # Log summary
        logger.info(f"Batch {batch_number} processing complete:")
        logger.info(f"  Total hemilineages: {results['total']}")
        
        if process_whole_neuron:
            wn = results['whole_neuron']
            logger.info(f"  Whole neuron - Successful: {wn['successful']}, Failed: {wn['failed']}, Skipped: {wn['skipped']}")
        
        if process_cbf:
            cb = results['cbf']
            logger.info(f"  CBF - Successful: {cb['successful']}, Failed: {cb['failed']}, Skipped: {cb['skipped']}")
        
        return results


def main():
    """Main function to run the batch processor."""
    parser = argparse.ArgumentParser(description='Process hemilineages from a specific batch with separate status tracking')
    
    parser.add_argument('batch_number', type=int, help='Batch number to process')
    parser.add_argument('--csv', default='hemileage_summary.csv', 
                       help='Path to hemileage summary CSV file (default: hemileage_summary.csv)')
    
    # Processing options
    parser.add_argument('--whole_neuron', action='store_true', 
                       help='Process whole neuron (CBF=False)')
    parser.add_argument('--cbf', action='store_true', 
                       help='Process CBF version (CBF=True)')
    parser.add_argument('--cbf_threshold', type=float, default=0.2,
                       help='Threshold for CBF processing (default: 0.2)')
    
    # Other options
    parser.add_argument('--template', default='JRC2018U',
                       help='Target brain template (default: JRC2018U)')
    parser.add_argument('--source', default='FLYWIRE',
                       help='Source coordinate system (default: FLYWIRE)')
    parser.add_argument('--update', action='store_true',
                       help='Force update of existing files')
    parser.add_argument('--no_skip_completed', action='store_true',
                       help='Process even completed hemilineages')
    
    args = parser.parse_args()
    
    # Validate that at least one processing type is selected
    if not (args.whole_neuron or args.cbf):
        logger.error("Must specify at least one of --whole_neuron or --cbf")
        sys.exit(1)
    
    # Create processor
    processor = HemilineageBatchProcessorV2(args.csv)
    
    # Process the batch
    results = processor.process_batch(
        batch_number=args.batch_number,
        process_whole_neuron=args.whole_neuron,
        process_cbf=args.cbf,
        cbf_threshold=args.cbf_threshold,
        template=args.template,
        source=args.source,
        update=args.update,
        skip_completed=not args.no_skip_completed
    )
    
    # Exit with error code if any processing failed
    total_failed = results['whole_neuron']['failed'] + results['cbf']['failed']
    if total_failed > 0:
        logger.warning(f"Exiting with error code due to {total_failed} failed processes")
        sys.exit(1)


if __name__ == '__main__':
    main()
