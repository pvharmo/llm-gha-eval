from ruamel.yaml import YAML
from pathlib import Path
from collections import OrderedDict

class GitHubActionsYAML:
    def __init__(self):
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.default_flow_style = False
        self.yaml.width = 9999
        self.yaml.indent(mapping=2, sequence=4, offset=2)

        # Define the preferred order of top-level keys
        self.top_level_order = [
            'name',
            'on',
            'permissions',
            'env',
            'defaults',
            'concurrency',
            'jobs'
        ]

        # Define the preferred order of job-level keys
        self.job_level_order = [
            'name',
            'needs',
            'runs-on',
            'environment',
            'concurrency',
            'outputs',
            'env',
            'defaults',
            'if',
            'permissions',
            'steps'
        ]

        # Define the preferred order of step-level keys
        self.step_level_order = [
            'name',
            'id',
            'if',
            'uses',
            'run',
            'with',
            'env',
            'continue-on-error',
            'timeout-minutes'
        ]

    def _sort_dict(self, d, order):
        """Sort dictionary based on specified key order."""
        # Create a new OrderedDict with keys in the specified order
        sorted_dict = OrderedDict()

        # First add keys that are in the order list
        for key in order:
            if key in d:
                sorted_dict[key] = d[key]

        # Then add any remaining keys that weren't in the order list
        for key in d:
            if key not in sorted_dict:
                sorted_dict[key] = d[key]

        return dict(sorted_dict)

    def _process_steps(self, steps):
        """Process and sort step-level configurations."""
        if not isinstance(steps, list):
            return steps

        return [self._sort_dict(step, self.step_level_order)
                if isinstance(step, dict) else step
                for step in steps]

    def _process_jobs(self, jobs):
        """Process and sort job-level configurations."""
        if not isinstance(jobs, dict):
            return jobs

        sorted_jobs = OrderedDict()
        for job_id, job_config in jobs.items():
            if isinstance(job_config, dict):
                # Sort job-level keys
                job_config = self._sort_dict(job_config, self.job_level_order)

                # Process steps if present
                if 'steps' in job_config:
                    job_config['steps'] = self._process_steps(job_config['steps'])

            sorted_jobs[job_id] = job_config

        return sorted_jobs

    def format_workflow(self, workflow_data):
        """Format the entire workflow with sorted keys."""
        # Sort top-level keys
        workflow = self._sort_dict(workflow_data, self.top_level_order)

        # Process jobs if present
        if 'jobs' in workflow:
            workflow['jobs'] = self._process_jobs(workflow['jobs'])

        return workflow

    def format_file(self, input_path, output_path=None):
        """Format a workflow file and optionally save to a new file."""
        input_path = Path(input_path)
        if output_path is None:
            output_path = input_path
        else:
            output_path = Path(output_path)

        # Read the workflow file
        with open(input_path, 'r') as f:
            workflow_data = self.yaml.load(f)

        # Format the workflow
        formatted_workflow = self.format_workflow(workflow_data)

        # Write the formatted workflow
        with open(output_path, 'w') as f:
            self.yaml.dump(formatted_workflow, f)

def main():
    # Example usage
    formatter = GitHubActionsYAML()

    # Example workflow
    # example_workflow = {
    #     'jobs': {
    #         'build': {
    #             'steps': [
    #                 {'run': 'echo "Hello"', 'name': 'Greeting'},
    #                 {'uses': 'actions/checkout@v2'},
    #             ],
    #             'runs-on': 'ubuntu-latest',
    #         }
    #     },
    #     'name': 'CI',
    #     'on': 'push',
    # }
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.default_flow_style = False
    yaml.width = 9999
    yaml.indent(mapping=2, sequence=4, offset=2)
    example_workflow = yaml.load(open("test2.yml").read())

    # Format the workflow
    formatted = dict(formatter.format_workflow(example_workflow))

    # Print the formatted workflow
    yaml.dump(formatted, sys.stdout)

if __name__ == '__main__':
    import sys
    main()
