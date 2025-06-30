// Parse arguments
args = split(getArgument());
inputPath = args[0];
outputFolder = args[1];
print(inputPath);
print(outputFolder);

// Open the image
open(inputPath);
print("image opened");

// set min to 2
run("Min...", "value=2 stack");

// Save original image with min as 2
run("Nrrd ... ", "nrrd=" + inputPath);


// Get the base name of the input file (without extension)
nameStart = lastIndexOf(inputPath, "/") + 1;
nameEnd = lastIndexOf(inputPath, ".");
baseName = substring(inputPath, nameStart, nameEnd);
print(baseName);

// Flip the image
run("Flip Horizontally", "stack");
print("image flipped");

// Save the flipped image as .nrrd in the output folder
flippedSavePath = outputFolder + "flipped_" + baseName + ".nrrd";
print("start saving flipped image: " + flippedSavePath);
run("Nrrd ... ", "nrrd=" + flippedSavePath);
print(flippedSavePath + " saved!");

// Close the image
close("*");
