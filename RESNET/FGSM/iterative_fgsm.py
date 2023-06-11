################################################################################
#                                                                              #
# This code runs iterative FGSM on an example image.                           #
# The algorithm was introduced in ADVERSARIAL EXAMPLES IN THE PHYSICAL WORLD,  #
# ICLR 2017.                                                                   #
#                                                                              #
# It produces adversarial images with quasi-imperctible perturbations          #
#                                                                              #
# Authors:  Jason Anderson <jand271@stanford.edu>                              #
#                                                                              #
# Usage: Run python iterative_fgsm.py                                          #
#                                                                              #
#                                                                              #
# Copyright 2023 Jason Anderson <jand271@stanford.edu>                         #
#                                                                              #
#                           MIT License                                        #
#                                                                              #
# Permission is hereby granted, free of charge, to any person obtaining a copy #
# of this software and associated documentation files (the “Software”), to     #
# deal in the Software without restriction, including without limitation the   #
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or  #
# sell copies of the Software, and to permit persons to whom the Software is   #
# furnished to do so, subject to the following conditions:                     #
#                                                                              #
# The above copyright notice and this permission notice shall be included in   #
# all copies or substantial portions of the Software.                          #
#                                                                              #
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND,              #
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF           #
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO #
# EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,        #
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR        #
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE    #
# USE OR OTHER DEALINGS IN THE SOFTWARE.                                       #
#                                                                              #
#                                                                              #
################################################################################

import timm
import torch
from PIL import Image
from timm.data import resolve_data_config
import torchvision.transforms as transforms
from timm.data.transforms_factory import create_transform
import matplotlib.pyplot as plt

from torchvision.transforms import Resize, CenterCrop, ToPILImage
from torchvision.transforms import Normalize, Compose


def inverse_transform(image):
    # inverse transform generated by request from ChatGPT by supplying the print(transform) from below
    inv_normalize = Normalize(
        mean=[-0.485 / 0.229, -0.456 / 0.224, -0.406 / 0.225],
        std=[1 / 0.229, 1 / 0.224, 1 / 0.225]
    )

    image = inv_normalize(image)
    image = ToPILImage()(image)
    image = CenterCrop(size=(235, 235))(image)
    image = Resize(size=(224, 224), interpolation=2)(image)
    return image


if __name__ == '__main__':

    # Load from Hub 🔥
    model = timm.create_model(
        'hf-hub:nateraw/resnet50-oxford-iiit-pet',
        pretrained=True
    )

    # Set model to eval mode for inference
    model.eval()

    # Create Transform
    transform = create_transform(**resolve_data_config(model.pretrained_cfg, model=model))

    # Get the labels from the model config
    # edit: was "label_names", now "labels"
    labels = model.pretrained_cfg['labels']
    top_k = min(len(labels), 5)

    # Use your own image file here...
    # image = Image.open('saint_bernard.jpg').convert('RGB')
    # target_label = torch.tensor([28])
    image = Image.open('Boxer-dog.jpg').convert('RGB')
    target_label = torch.tensor([8])
    print(f"Original Label: {labels[target_label]}")

    # Process PIL image with transforms and add a batch dimension
    x = transform(image).unsqueeze(0)
    x_init = x.data
    x.requires_grad = True

    epsilon = 1e-3

    for i in range(100):

        y_pred = model(x)

        if y_pred.argmax() != target_label:
            break

        loss = torch.nn.functional.cross_entropy(y_pred, target_label)

        model.zero_grad()

        loss.backward()

        dx = x.grad.sign()

        x.data = x.data + epsilon * dx.data

    #Apply softmax to get predicted probabilities for each class
    probabilities = torch.nn.functional.softmax(y_pred[0], dim=0)

    # Grab the values and indices of top 5 predicted classes
    values, indices = torch.topk(probabilities, top_k)

    # Prepare a nice dict of top k predictions
    predictions = [
        {"label": labels[i], "score": v.item()}
        for i, v in zip(indices, values)
    ]
    print(predictions)

    # Display initial image
    plt.imshow(image)
    plt.axis('off')
    plt.show()

    # Display final image
    final_image = inverse_transform(x.squeeze())
    plt.imshow(final_image)
    plt.axis('off')
    plt.show()

    # diff
    diff_image = inverse_transform((x - x_init).squeeze())
    plt.imshow(diff_image)
    plt.axis('off')
    plt.show()