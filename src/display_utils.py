import matplotlib.pyplot as plt
from collections import defaultdict
import torch
from transformers import (
    DetrForObjectDetection,
    ConditionalDetrForObjectDetection,
    DeformableDetrForObjectDetection,
)
import numpy as np
from datasets import Dataset
from torchvision.ops import box_convert
from torchvision.transforms.functional import pil_to_tensor, to_pil_image
from torchvision.utils import draw_bounding_boxes



# colors for visualization
COLORS = [
    [0.000, 0.447, 0.741],
    [0.850, 0.325, 0.098],
    [0.929, 0.694, 0.125],
    [0.494, 0.184, 0.556],
    [0.466, 0.674, 0.188],
    [0.301, 0.745, 0.933],
]


## Show only top prob
def detr_plot_results1(pil_img, prob, boxes, model: DetrForObjectDetection):
    plt.figure(figsize=(16, 10))
    plt.imshow(pil_img)
    ax = plt.gca()
    colors = COLORS * 100

    # Store the highest probability per text category
    highest_prob = defaultdict(lambda: (0, None, None))
    for p, box, c in zip(prob, boxes.tolist(), colors):
        cl = p.argmax()
        if p[cl] > highest_prob[cl.item()][0]:
            highest_prob[cl.item()] = (p[cl], box, c) # type: ignore

    # Plot only the bounding box with the highest probability per text category
    for cl, (p, (xmin, ymin, xmax, ymax), c) in highest_prob.items(): # type: ignore
        ax.add_patch(
            plt.Rectangle(
                (xmin, ymin), xmax - xmin, ymax - ymin, fill=False, color=c, linewidth=3
            )
        )
        text = f"{model.config.id2label[cl]}: {p:0.2f}"
        ax.text(xmin, ymin, text, fontsize=10, color="red")

    plt.axis("off")
    plt.show()


def detr_plot_results2(pil_img, prob, boxes, model: DetrForObjectDetection):
    plt.figure(figsize=(16, 10))
    plt.imshow(pil_img)
    ax = plt.gca()
    colors = COLORS * 100
    for p, (xmin, ymin, xmax, ymax), c in zip(prob, boxes.tolist(), colors):
        ax.add_patch(
            plt.Rectangle(
                (xmin, ymin), xmax - xmin, ymax - ymin, fill=False, color=c, linewidth=3
            )
        )
        cl = p.argmax()
        text = f"{model.config.id2label[cl.item()]}: {p[cl]:0.2f}"
        print(text)
        ax.text(
            xmin,
            ymin,
            text,
            fontsize=10,
            color="red",
            bbox=dict(facecolor="None", alpha=0.5),
        )
    plt.axis("off")
    plt.show()


def plot_results_all(
    pil_img,
    boxes,
    labels,
    scores,
    model: ConditionalDetrForObjectDetection | DeformableDetrForObjectDetection,
    colors=None,
):
    plt.figure(figsize=(16, 10))
    plt.imshow(pil_img)
    ax = plt.gca()

    if colors is None:
        colors = plt.cm.hsv(np.linspace(0, 1, len(boxes))).tolist()

    for box, label, score, color in zip(boxes, labels, scores, colors):
        xmin, ymin, xmax, ymax = box.detach().numpy()
        ax.add_patch(
            plt.Rectangle(
                (xmin, ymin),
                xmax - xmin,
                ymax - ymin,
                fill=False,
                color=color,
                linewidth=3,
            )
        )

        text = f"{model.config.id2label[label.item()]}: {score:0.2f}"
        ax.text(xmin, ymin, text, fontsize=10, color="red")

    plt.axis("off")
    plt.show()


def print_dataset(dataset: Dataset):
    for i in range(len(dataset)):
        item = dataset[i]
        print(f"Item {i}:")
        print(item)


def show_image_bbox_dataset(index, dataset, categories):
  example = dataset[index]

  boxes_xywh = torch.tensor(example['objects']['bbox'])
  boxes_xyxy = box_convert(boxes_xywh, 'xywh', 'xyxy')
  print(boxes_xyxy, boxes_xywh)
  labels = [categories[x] for x in example['objects']['categories']]
  display(to_pil_image(
      draw_bounding_boxes(
          pil_to_tensor(example['image']),
          boxes_xyxy,
          colors="red",
          labels=labels,
      )
  ))