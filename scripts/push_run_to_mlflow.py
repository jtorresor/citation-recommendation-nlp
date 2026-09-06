import argparse
import tempfile
import zipfile
from pathlib import Path

import mlflow


def read_run(run_dir: Path):
    params = {p.name: p.read_text().strip() for p in (run_dir / "params").iterdir()}
    metrics = {}
    for m in (run_dir / "metrics").iterdir():
        last = m.read_text().strip().splitlines()[-1]
        metrics[m.name] = float(last.split()[1])
    tags = {
        t.name: t.read_text().strip()
        for t in (run_dir / "tags").iterdir()
        if not t.name.startswith("mlflow.")
    }
    return params, metrics, tags


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", required=True)
    ap.add_argument("--uri", required=True)
    ap.add_argument("--experiment", default="intencite-model-comparison")
    ap.add_argument("--run-name", default="llm-lora-3ctx-v1")
    ap.add_argument("--with-adapter", action="store_true")
    args = ap.parse_args()

    with tempfile.TemporaryDirectory() as tmp:
        with zipfile.ZipFile(args.zip) as z:
            z.extractall(tmp)

        run_dirs = list(Path(tmp).glob("content/mlruns/*/*/params"))
        run_dir = run_dirs[0].parent
        params, metrics, tags = read_run(run_dir)

        mlflow.set_tracking_uri(args.uri)
        mlflow.set_experiment(args.experiment)

        with mlflow.start_run(run_name=args.run_name) as run:
            mlflow.log_params(params)
            mlflow.log_metrics(metrics)
            mlflow.set_tags(tags)
            mlflow.log_artifacts(str(run_dir / "artifacts" / "evaluation"), "evaluation")
            if args.with_adapter:
                mlflow.log_artifacts(str(run_dir / "artifacts" / "lora_adapter"), "lora_adapter")

            print("run_id:", run.info.run_id)
            print("uri:", args.uri)
            print("params:", params)
            print("metrics:", metrics)


if __name__ == "__main__":
    main()
