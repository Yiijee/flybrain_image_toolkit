//parse arguments
args = split(getArgument());
inputPath = args[0];
outputFolder = args[1];
print(inputPath);
print(outputFolder);


// Open the image
open(inputPath);
print('image opened');
// Get the base name of the input file (without extension)
nameStart = lastIndexOf(inputPath, "/") + 1;
nameEnd = lastIndexOf(inputPath, ".");
baseName = substring(inputPath, nameStart, nameEnd);
print(baseName);
imagetitle = getTitle();
// Split channels
run("Split Channels");
print("channel splitted");
// Save each channel as .nrrd in the output folder
for (i = 1; i <= nImages; i++) {
    selectImage("C"+i+"-"+imagetitle); // Select each channel
    savePath = outputFolder + baseName + "_ch" + i + ".nrrd";
    print("start saving" + savePath);
    run("Nrrd ... ", "nrrd=" + savePath);
    print(savePath + " saved!"); 
}
close("*");
