
import os

project_root_path = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

print(os.path.join(project_root_path, "data"))

id_list = os.listdir(os.path.join(project_root_path, "data", "human1000"))
id_list = sorted(id_list)
with open("human1000_upd.txt", "w") as f:
    for idd in id_list:
        f.write(idd.split(".json")[0]+ "\n")