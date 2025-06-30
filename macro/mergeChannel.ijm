//parse arguments
print(getArgument());
imageTitles = split(getArgument());
cmd = "";
for (i = 0; i < imageTitles.length; i++) {
	open(imageTitles[i]);
	title = getTitle();
	print("image opened");
	cmd = cmd + "c"+ i+3 + "="+title+" ";
	//selectImage(imageTitles[i]);
	run("8-bit");
}
// Get the base name of the input file (without extension)
nameStart = lastIndexOf(imageTitles[0], "/") + 1;
nameEnd = lastIndexOf(imageTitles[0], "_");
baseName = substring(imageTitles[0], nameStart, nameEnd);

run("Merge Channels...", cmd + "create");
saveAs("Tiff",baseName+".tif")


