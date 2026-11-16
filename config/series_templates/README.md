# Series templates

Each JSON file is a 24-page review-sample configuration for one of the requested general themes. Select a template in the GitHub Actions KDP Production Pipeline input or run the pipeline locally with --config.

The built-in generator provides 12 distinct motifs per theme for review samples. A 100-page production volume requires exactly 50 approved, distinct original assets in assets/images/<theme>/. The pipeline refuses to repeat or pad the art set. After all 50 assets are supplied and rights-reviewed, update page_count to 100 and illustration_count to 50.
