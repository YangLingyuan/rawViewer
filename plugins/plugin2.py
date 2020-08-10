def run(RawProcessor,image):
    RawProcessor.loadImage("plugin2")
    image = image + 10
    print("Processed image is %d"%image)