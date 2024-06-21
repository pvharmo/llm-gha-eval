from github import Github
from github import GithubException, UnknownObjectException
import streamlit as st
from menu import menu
from env import gh_token
import pandas as pd
import os
import json
from stqdm import stqdm
import msgspec

from github import Auth

st.set_page_config(
    page_title="Build dataset",
    page_icon="📑",
    layout="wide",
    initial_sidebar_state="expanded",
)

menu()

stqdm.pandas()

st.title("📑 Visualize benchmarks")

encoder = msgspec.json.Encoder()

def has_common_element(list1, list2):
    return any(element in list2 for element in list1)

def get_repo_data(g: Github, repo_data, container):
    with container:
        path_exists = os.path.exists(f"./dataset/repos/{repo_data['name']}")
        if path_exists or repo_data["isArchived"] or repo_data["isDisabled"]:
            st.write(f"Skipping {repo_data['name']}, {'path exists' if path_exists else ('is archived' if repo_data['isArchived'] else 'is disabled')}")
            return

        repo = g.get_repo(repo_data["name"])

        st.write(f"Processing {repo_data['name']}")

        try:
            contents = repo.get_contents("/.github/workflows")
        except UnknownObjectException as e:
            st.write("No workflows found")
            return
        
        st.write(f"Found {len(contents)} workflows")
        
        if len(contents) <= 2:
            return

        os.makedirs(f"./dataset/repos/{repo_data['name']}/workflows", exist_ok=True)
        os.makedirs(f"./dataset/repos/{repo_data['name']}/configs", exist_ok=True)

        for content in contents:
            if content.type != "file":
                continue
            file = repo.get_contents(content.path).decoded_content.decode("utf-8")
            with open(f'./dataset/repos/{repo_data["name"]}/workflows/{content.path.split("/")[-1]}', 'w') as f:
                f.write(file)

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
                    if content.type != "file":
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

def build_dataset(nb_repo):
    repos = pd.read_csv("./config/results-1500-stars-20-june.csv")

    auth = Auth.Token(gh_token)
    g = Github(auth=auth)

    # r = {
    #     "name": "hashicorp/setup-terraform",
    #     "isArchived": False,
    #     "isDisabled": False,
    #     "defaultBranch": "main"
    # }
    # get_repo_data(g, r)

    container = st.container(height=900)
    repos.loc[(repos["isArchived"] == False) & (repos["isDisabled"] == False)].sample(nb_repo).progress_apply(lambda repo_data: get_repo_data(g, repo_data, container), axis=1)

    g.close()

nb_repo = st.number_input("Number of repositories to fetch", value=50, min_value=1, max_value=100000)
st.button("Start", on_click=lambda: build_dataset(nb_repo))