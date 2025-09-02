import os, sys

def flip4ByteEndian(hexString):
    return hexString[6:8] + hexString[4:6] + hexString[2:4] + hexString[0:2]

def main():
    # Get inputted files
    inputFiles = sys.argv[1:]
    for inputFile in inputFiles:
        try:
            inputSize = os.path.getsize(inputFile)
        except FileNotFoundError:
            print(inputFile + " cannot be found.")
            return 0
        
        inputFileName, inputFileExt = os.path.splitext(inputFile)
        
        if (inputFileExt != ".tmx"):
            print(inputFile + " is not a tmx file!")
        else:
            with open(inputFile, "rb") as tmxFile:
                # Get the TMX files offset and the starting offset
                tmxFile.seek(88)
                packageFilesInfoOffset = int(flip4ByteEndian(tmxFile.read(4).hex()),16)
                packageFilesOffset = int(flip4ByteEndian(tmxFile.read(4).hex()),16)
                
                # Parse the TMX files info and get the offsets of each currentFile
                tmxFile.seek(packageFilesInfoOffset)
                packageFilesInfoString = tmxFile.read(packageFilesOffset - packageFilesInfoOffset).hex()
                packageFilesInfo = list()
                while (packageFilesInfoString != ''):
                    # 204e4947 = NIG. I'm sorry
                    if (packageFilesInfoString[:8] == "204e4947"):
                        fileType = "GIN"
                    else:
                        fileType = "SNR"
                        
                    packageFilesInfo += [ { fileType: int(flip4ByteEndian(packageFilesInfoString[16:24]),16) + packageFilesOffset } ]
                    
                    packageFilesInfoString = packageFilesInfoString[72:]
                
                # Extract the files (note the extraction isnt perfect and doesn't account for random 00 padding bytes)
                for i in range(len(packageFilesInfo)):
                    currentFileInfo = packageFilesInfo[i]
                    nextFileInfo = {}
                    if (i+1 < len(packageFilesInfo)):
                        nextFileInfo = packageFilesInfo[i+1]
                        
                    currentFileType =  list(currentFileInfo.keys())[0]
                    
                    currentFileName = inputFileName + "-" + str(i) + "." + currentFileType
                    
                    with open( currentFileName, 'wb') as currentFile:
                        
                        tmxFile.seek(currentFileInfo[currentFileType])
                        
                        if (nextFileInfo == {}):
                            currentFileLength = inputSize - currentFileInfo[currentFileType]
                        else:
                            currentFileLength = list(nextFileInfo.values())[0] - currentFileInfo[currentFileType]
                            
                        content = bytes.fromhex(tmxFile.read(currentFileLength).hex())
                        
                        currentFile.write(content)
                        
                    currentFile.close()
                    print(currentFileName + " exported!")
                    
                            
            tmxFile.close()


if __name__=="__main__":
    main()