from datasets import load_dataset, Dataset


original_dataset = load_dataset("./new")

train = original_dataset["train"]

new_train = []
for row in train:
    new_train.append(
        {
            "english": row["English"],
            "twi": row["Twi"],
        }
    )

new_dataset = Dataset.from_list(new_train)
new_dataset.to_json("./dataset/processed_dataset.json")
