#!/usr/bin/env python

from utils import *

if __name__ =='__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('--epochs', type=int, default=2)
    parser.add_argument('--batch-size', type=int, default=32)
    parser.add_argument('--gpus', type=int, default=1)
    parser.add_argument('--num-workers', type=int, default=8)
    parser.add_argument('--lr', type=float, default=1e-3)
    parser.add_argument('--milestone', type=int, default=5)
    parser.add_argument('--backbone', type=str, default="x3d_s")
    parser.add_argument('--resize', type=int, default=0)
    parser.add_argument('--unfreeze_top_layers', type=int, default=3)
    parser.add_argument('-o','--output-data-dir', type=str, default='/opt/ml/output/data')
    parser.add_argument('--train', type=str, default='/opt/ml/input/data/train')

    args = parser.parse_args()

    config = {"lr": args.lr,
              "batch_size": args.batch_size,
              "num_workers": args.num_workers,
              "milestone": args.milestone,
              "epochs": args.epochs,
              "backbone": args.backbone,
              "resize": args.resize,
              "unfreeze_top_layers": args.unfreeze_top_layers,}

    finetuning_callback = MilestonesFinetuning(milestone=config["milestone"], unfreeze_top_layers=config["unfreeze_top_layers"], train_bn=False)
    wandb_logger = WandbLogger(project='deepfake', offline=False, name=config["backbone"], config=config)

    trainer = pl.Trainer(gpus=args.gpus, 
                        max_epochs=config["epochs"], 
                        callbacks=[finetuning_callback],
                        log_every_n_steps=25,
                        amp_level='O2', 
                        precision=16,
                        default_root_dir=args.output_data_dir,
                        logger=wandb_logger,
                        )

    model = DeepFakeModel(backbone=config["backbone"], 
                         lr=config["lr"], 
                         milestone=config["milestone"])

    data = DeepFakeDataModule(data_path=args.train,
                              backbone=config["backbone"], 
                              batch_size=config["batch_size"], 
                              num_workers=config["num_workers"], 
                              resize=config["resize"])
    
    trainer.fit(model, data)
    