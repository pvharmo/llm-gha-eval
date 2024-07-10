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

from assistant import Assistant
import env

st.set_page_config(
    page_title="Build dataset",
    page_icon="📑",
    layout="wide",
    initial_sidebar_state="expanded",
)

menu()

stqdm.pandas()

st.title("📑 Visualize benchmarks")

count = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen", "twenty"]

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
            contents: list[ContentFile.ContentFile] = repo.get_contents("/.github/workflows") # type: ignore
        except UnknownObjectException as e:
            st.write("No workflows found")
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
                workflows.append({
                    "owner": owner,
                    "repo_name": repo_name,
                    "workflow_file": workflow_file,
                    "directory": directory
                })

    for workflow_infos in stqdm(workflows):
        directory = workflow_infos["directory"]
        workflow_file = workflow_infos["workflow_file"]

        with open(directory + "/workflows/" + workflow_file) as file:
            content = file.read()

        try:
            workflow = yaml.safe_load(content)
        except:
            continue

        try:
            if "name" not in workflow.keys() or "jobs" not in workflow.keys() or os.path.exists(directory + "/detailed_descriptions/" + workflow_file + ".md"):
                continue
        except:
            continue

        valid_workflow = True

        for job in workflow["jobs"]:
            if "steps" not in workflow["jobs"][job].keys():
                valid_workflow = False
                break
            for step in workflow["jobs"][job]["steps"]:
                if "name" not in step.keys():
                    valid_workflow = False
                    break
                    break

        if not valid_workflow:
            continue

        st.write("# " + workflow_infos["owner"] + "/" + workflow_infos["repo_name"] + " - " + workflow_file)
        with open(directory + "/properties.json", 'r') as file:
            meta_data = json.load(file)

        languages = meta_data['languages']

        main_language = max(languages, key=languages.get)
        description = f'Generate a GitHub Workflow named {workflow["name"]} for a GitHub repository whose programming language is {main_language}.'
        job_ids = f' The workflow has {count[len(workflow["jobs"])]} job{"s" if len(workflow["jobs"]) > 1 else ""}.'
        step_names = ""
        for i, job_name in enumerate(workflow["jobs"]):
            job = workflow["jobs"][job_name]
            job_ids += f' The job id of the {i+1}{"st" if i == 0 else "nd" if i == 1 else "rd" if i == 2 else "th"} job is "{job_name}".'

            step_names = f' The job {job_name} has {count[len(job["steps"])]} step{"s" if len(job["steps"]) > 1 else ""}.'
            for i, step in enumerate(job["steps"]):
                step_names += f' The {i+1}{"st" if i == 0 else "nd" if i == 1 else "rd" if i == 2 else "th"} step is named "{step["name"]}".'

        st.write(description)
        st.write(job_ids)
        st.write(step_names)

        # assistant_explainer_workflow_level = Assistant(
        #     model="Qwen/Qwen2-72B-Instruct",
        #     system_prompt="""
        #         Tell me on which events it should trigger. Here is an example of the expected answer:
        #             This workflow will be triggered by an event: The workflow would run whenever there is a push event to a branch named “main”.
        #         """
        # )

        # assistant_explainer_jobs_infos = Assistant(
        #     model="Qwen/Qwen2-72B-Instruct",
        #     system_prompt="""
        #         Tell me The informations about each jobs except for the steps and the name of the job. Here is an example of the expected answer:
        #             The job “build” runs on ubuntu-latest runner.
        #         """
        # )

        # assistant_explainer_steps_infos = Assistant(
        #     model="Qwen/Qwen2-72B-Instruct",
        #     system_prompt="""
        #         Tell me the name of each steps for each jobs. Here is an example of the expected answer:
        #             The job “build” has 5 steps. The 1st step is named “Checkout sources”. The 2nd step is named “Install
        #             stable toolchain”. The 3rd step is named “Run cargo build”. The 4th step is named “Prepare docs
        #             folder”. The 5th step is named “Deploy documentation branch”.
        #         """
        # )

        # original_workflow_description = assistant_explainer_p1.run(content)

        # if not os.path.exists(directory + "/detailed_descriptions"):
        #     os.makedirs(directory + "/detailed_descriptions")

        # with open(directory + "/detailed_descriptions/" + workflow_file + ".md", "w") as file:
        #     file.write(original_workflow_description)

st.button("Create detailed descriptions", on_click=lambda: create_detailed_descriptions())
st.button("Create article descriptions", on_click=lambda: create_article_descriptions())
