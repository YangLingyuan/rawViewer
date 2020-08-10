def run(RawProcessor,image):
    RawProcessor.loadImage("plugin1")
    image = image + 1
    print("Processed image is %d"%image)