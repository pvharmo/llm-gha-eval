import os
import datetime
from time import sleep
from github import UnknownObjectException, ContentFile, Github
from env import gh_token
import pandas as pd
import os
import msgspec
from github import Auth
from tqdm import tqdm

start_time = datetime.datetime.now()
print(f"Started at {start_time}")

tqdm.pandas()

encoder = msgspec.json.Encoder()

def has_common_element(list1, list2):
    return any(element in list2 for element in list1)

def get_repo_data(g: Github, repo_data):
    try:
        with open(f'./config/repos-1-year_repos_done.csv') as file:
            content = file.read()

        if repo_data['name'] in (line.strip() for line in content.splitlines()):
            return

        path_exists = os.path.exists(f"./dataset/repos/{repo_data['name']}")
        if path_exists or repo_data["isArchived"] or repo_data["isDisabled"]:
            print(f"Skipping {repo_data['name']}, {'path exists' if path_exists else ('is archived' if repo_data['isArchived'] else 'is disabled')}")
            with open(f'./config/repos-1-year_repos_done.csv', "+a") as f:
                f.write(f"{repo_data['name']}\n")
            return

        sleep(4)
        repo = g.get_repo(repo_data["name"])

        try:
            contents: list[ContentFile.ContentFile] = repo.get_contents("/.github/workflows") # type: ignore
        except UnknownObjectException as e:
            print(f"Error processing {repo_data['name']}: UnknownObjectException")
            with open(f'./config/repos-1-year_repos_done.csv', "+a") as f:
                f.write(f"{repo_data['name']}\n")
            return

        os.makedirs(f"./dataset/repos/{repo_data['name']}/workflows", exist_ok=True)
        os.makedirs(f"./dataset/repos/{repo_data['name']}/configs", exist_ok=True)

        for content in contents:
            if content.type != "file":
                continue
            file = repo.get_contents(content.path).decoded_content.decode("utf-8") # type: ignore
            with open(f'./dataset/repos/{repo_data["name"]}/workflows/{content.path.split("/")[-1]}', 'w') as f:
                f.write(file) # type: ignore

        tree = repo.get_git_tree(repo_data["defaultBranch"], recursive=True)
        tree = [t.path for t in tree.tree]

        with open(f'./dataset/repos/{repo_data["name"]}/tree.csv', 'w') as f:
            f.write("\n".join(tree))

        try:
            license = repo.get_license()
        except:
            license = None

        properties = {
            "license": license.license.name if license else "No license",
            "defaultBranch": repo_data["defaultBranch"],
            "languages": repo.get_languages(),
            "tree_truncated": len(tree) == 100000,
            "package_specs": {
                "package.json": [], # Node, Bun, Deno
                "requirements": [], # Python
                "pyproject.toml": [], # Python
                "cargo.toml": [], # Rust
                "go.mod": [], # Go
                "pom.xml": [], # Maven
                "build.gradle": [], # Gradle
                ".csproj": [], # .NET
                "packages.config": [], # .NET
                "composer.json": [], # PHP
                "Gemfile": [], # Ruby
                "CMakeLists.txt": [], # C/C++
                "Makefile": [], # C/C++
                "Dockerfile": [], # Docker
                "docker-compose.yml": [], # Docker
            }
        }

        ignored_dirs = [
            "packages",
            "node_modules",
            "jspm_packages",
            "bower_components",
            "web_modules",
            ".cache",
            "share",
            "__pypackages__",
            "venv",
            "vendor",
            "target",
            "debug",
            "build",
            "dist",
            "out",
            "bin",
            "obj",
            "static",
            "public",
            "public_html",
            ".gradle",
            "_deps",
            "third_party",
            "third-party",
            "thirdparty",
            "third-parties",
            "thirdparties",
        ]

        for t in tree:
            has_common_element(t.split("/"), ignored_dirs)
            for spec in properties["package_specs"].keys():
                if spec in t:
                    file = repo.get_contents(t)
                    if isinstance(file, list) or file.type != "file":
                        continue
                    try:
                        with open(f'./dataset/repos/{repo_data["name"]}/configs/{len(properties["package_specs"][spec])}-{spec}', 'w') as f:
                            f.write(file.decoded_content.decode("utf-8"))
                    except:
                        pass
                    properties["package_specs"][spec].append(t)

        with open(f'./dataset/repos/{repo_data["name"]}/properties.json', 'wb') as f:
            msgpack = encoder.encode(properties)
            f.write(msgpack)

        with open(f'./config/repos-1-year_repos_done.csv', "+a") as f:
            f.write(f"{repo_data['name']}\n")
    except Exception as e:
        print(f"Error on {repo_data['name']}: {e}")

def build_dataset(nb_repo):
    repos = pd.read_csv("./config/repos-1-year.csv")

    auth = Auth.Token(gh_token)
    g = Github(auth=auth)

    repos.loc[(repos["isArchived"] == False) & (repos["isDisabled"] == False)].sample(nb_repo).progress_apply(lambda repo_data: get_repo_data(g, repo_data), axis=1)

    g.close()


nb_repo = 2500
build_dataset(nb_repo)

# print current time
print(f"Ended at ", datetime.datetime.now())
# print time taken
print("Time taken: ", datetime.datetime.now() - start_time)
