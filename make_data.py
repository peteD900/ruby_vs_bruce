import pandas as pd
import os

def load_data(person: str):
    path = "./data"
    file_path = os.path.join(path, f"{person}.csv")
    return pd.read_csv(file_path)

def load_all_data(people = ["dad", "ruby", "bruce"]):
    data_list = [load_data(person) for person in people]
    df = pd.concat(data_list)
    return df

if __name__ == "__main__":
    df = load_all_data()
    print(df)