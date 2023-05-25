from typing import Optional, Union
from tqdm.auto import tqdm
import torch

from torch.utils.data import DataLoader
from transformers import (
    image_transforms,
    ConditionalDetrForObjectDetection,
    DeformableDetrForObjectDetection,
    ConditionalDetrImageProcessor,
    DeformableDetrImageProcessor
)
from torchmetrics.detection.mean_ap import MeanAveragePrecision
import display_utils
from datasets import Dataset


def run_evaluation_cond(
    model: Union[ConditionalDetrForObjectDetection, DeformableDetrForObjectDetection],
    feature_extractor: Union[ConditionalDetrImageProcessor, DeformableDetrImageProcessor],
    test_dataloader: DataLoader,
    device: torch.device,
    plot: bool = False,
    dataset: Optional[Dataset] = None,
):
    metric = MeanAveragePrecision(iou_type="bbox", class_metrics=True)
    model.to(device)
    model.eval()

    if plot and test_dataloader.batch_size != 1:
        raise ValueError("Plotting only works with batch size of 1")

    with torch.no_grad():
        for idx, batch in enumerate(tqdm(test_dataloader)):
            pixel_values = batch["pixel_values"].to(device)
            pixel_mask = batch["pixel_mask"].to(device)

            labels = [{k: v.to(device) for k, v in t.items()} for t in batch["labels"]]

            target_sizes = torch.stack([label["orig_size"] for label in labels], dim=0)

            img_h, img_w = target_sizes.unbind(1)
            scale_fct = torch.stack([img_w, img_h, img_w, img_h], dim=1).to(device)

            for label in labels:
                label["labels"] = label["class_labels"]
                label["boxes"] = (
                    image_transforms.center_to_corners_format(label["boxes"])
                    * scale_fct[0, None, :]
                )

            outputs = model(pixel_values=pixel_values, pixel_mask=pixel_mask)
            result = feature_extractor.post_process_object_detection(
                outputs, threshold=0.5, target_sizes=target_sizes
            )

            if plot:
                
                if not dataset:
                    raise ValueError("Dataset must be provided for plotting")

                display_utils.plot_results_all(
                    dataset["test"][idx]["image"],
                    result[0]["boxes"],
                    result[0]["labels"],
                    result[0]["scores"],
                    model=model,
                )
                display_utils.plot_results_all(
                    dataset["test"][idx]["image"],
                    labels[0]["boxes"],
                    labels[0]["labels"],
                    [1 for _ in range(len(labels[0]["boxes"]))],
                    model=model,
                )

            metric.update(result, labels)

    # print("Computing metric...")
    metric = metric.to(device)
    result = metric.compute()
    # print(result)
    return result
