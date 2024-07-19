from github import GithubException, UnknownObjectException, ContentFile, Github
import streamlit as st
from menu import menu
from env import gh_token
import pandas as pd
import os
import json
from stqdm import stqdm
import msgspec
from github import Auth
import yaml

from utils.count import count
from assistant import Assistant
import env
from utils.description import generate_description, prepare_workflow

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
    try:
        with open(f'./config/repos-1-year_repos_done.csv') as file:
            content = file.read()

        if repo_data['name'] in (line.strip() for line in content.splitlines()):
            return

        with container:
            path_exists = os.path.exists(f"./dataset/repos/{repo_data['name']}")
            if path_exists or repo_data["isArchived"] or repo_data["isDisabled"]:
                st.write(f"Skipping {repo_data['name']}, {'path exists' if path_exists else ('is archived' if repo_data['isArchived'] else 'is disabled')}")
                with open(f'./config/repos-1-year_repos_done.csv', "+a") as f:
                    f.write(f"{repo_data['name']}\n")
                return

            repo = g.get_repo(repo_data["name"])

            st.write(f"Processing {repo_data['name']}")

            try:
                contents: list[ContentFile.ContentFile] = repo.get_contents("/.github/workflows") # type: ignore
            except UnknownObjectException as e:
                st.write("No workflows found")
                with open(f'./config/repos-1-year_repos_done.csv', "+a") as f:
                    f.write(f"{repo_data['name']}\n")
                return

            st.write(f"Found {len(contents)} workflows")

            # if len(contents) <= 2:
            #     return

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
        st.write(f"Error on {repo_data['name']}: {e}")
        # with open(f'./config/repos-1-year_repos_done.csv', "+a") as f:
        #     f.write(f"{repo_data['name']}\n")

def build_dataset(nb_repo):
    repos = pd.read_csv("./config/repos-1-year.csv")

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

def create_detailed_descriptions():
    workflows = []

    for owner in stqdm(os.listdir(env.repository_directories)):
        for repo_name in os.listdir(env.repository_directories + "/" + owner):
            directory = env.repository_directories + "/" + owner + "/" + repo_name
            for workflow_file in os.listdir(directory + "/workflows"):
                workflows.append({
                    "owner": owner,
                    "repo_name": repo_name,
                    "workflow_file": workflow_file,
                    "directory": directory
                })

    for workflow_infos in stqdm(workflows):
        directory = workflow_infos["directory"]
        workflow_file = workflow_infos["workflow_file"]

        st.write(workflow_infos["directory"])

        if os.path.exists(directory + "/detailed_descriptions/" + workflow_file + ".md"):
            continue

        assistant_explainer = Assistant(
            model="Qwen/Qwen2-72B-Instruct",
            system_prompt="""
                You will be given a github actions workflow and you will have to explain what it does. Add enough details so the exact workflow can be reproduced only from this description.
                """
        )

        with open(directory + "/workflows/" + workflow_file) as file:
            content = file.read()

        original_workflow_description = assistant_explainer.run(content)

        if not os.path.exists(directory + "/detailed_descriptions"):
            os.makedirs(directory + "/detailed_descriptions")

        with open(directory + "/detailed_descriptions/" + workflow_file + ".md", "w") as file:
            file.write(original_workflow_description)

def create_article_descriptions():
    workflows = []

    for owner in stqdm(os.listdir(env.repository_directories)):
        for repo_name in os.listdir(env.repository_directories + "/" + owner):
            directory = env.repository_directories + "/" + owner + "/" + repo_name
            for workflow_file in os.listdir(directory + "/workflows"):
                if workflow_file.endswith(".yml") or workflow_file.endswith(".yaml"):
                    workflows.append({
                        "owner": owner,
                        "repo_name": repo_name,
                        "workflow_file": workflow_file,
                        "directory": directory
                    })

    nb_workflows = 0
    for workflow_infos in stqdm(workflows):
        prepare_workflow(workflow_infos)
        nb_workflows += 1
        break

    st.write("number of workflows: ", nb_workflows)

st.button("Create detailed descriptions", on_click=lambda: create_detailed_descriptions())
st.button("Create article descriptions", on_click=lambda: create_article_descriptions())
