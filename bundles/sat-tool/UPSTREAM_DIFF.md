# Upstream Diff: Local SAT Tool vs Databricks SAT

**Generated:** 2026-02-18 22:40 UTC
**Upstream repo:** https://github.com/databricks-industry-solutions/security-analysis-tool.git
**Upstream commit:** 6978257 (2026-02-18 15:55:43 -0500)
**Local SAT SDK version:** 0.1.38

---

## Upstream Directory Structure

```
./.github/ISSUE_TEMPLATE/bug_report.yml
./.github/ISSUE_TEMPLATE/config.yml
./.github/ISSUE_TEMPLATE/doc_request.yml
./.github/ISSUE_TEMPLATE/feature_request.yml
./.github/ISSUE_TEMPLATE/general_issue.md
./.github/pull_request_template.md
./.github/workflows/security-scan.yml
./.gitignore
./CHANGELOG.md
./CONTRIBUTING.md
./LICENSE
./NOTICE
./README.md
./SECURITY.md
./VERSIONING.md
./app/brickhound/README.md
./app/brickhound/app.py
./app/brickhound/app.yaml
./app/brickhound/databricks.yml
./app/brickhound/requirements.txt
./configs/sat_dasf_mapping.csv
./configs/security_best_practices.csv
./configs/self_assessment_checks.yaml
./configs/trufflehog_detectors.yaml
./dabs/dabs_template/databricks_template_schema.json
./dabs/dabs_template/template/tmp/databricks.yml.tmpl
./dabs/dabs_template/template/tmp/resources/brickhound_job.yml.tmpl
./dabs/dabs_template/template/tmp/resources/sat_driver_job.yml.tmpl
./dabs/dabs_template/template/tmp/resources/sat_initiliazer_job.yml.tmpl
./dabs/dabs_template/template/tmp/resources/sat_secrets_scanner_job.yml.tmpl
./dabs/main.py
./dabs/requirements.txt
./dabs/sat/__init__.py
./dabs/sat/config.py
./dabs/sat/utils.py
./dabs/setup.sh
./dashboards/SAT_Dashboard_definition.json
./docs/.gitignore
./docs/sat/.gitignore
./docs/sat/docs/faq.mdx
./docs/sat/docs/functionality.mdx
./docs/sat/docs/installation/index.mdx
./docs/sat/docs/installation/standard/aws.mdx
./docs/sat/docs/installation/standard/azure.mdx
./docs/sat/docs/installation/standard/gcp.mdx
./docs/sat/docs/installation/standard/index.mdx
./docs/sat/docs/installation/terraform/aws.mdx
./docs/sat/docs/installation/terraform/azure.mdx
./docs/sat/docs/installation/terraform/gcp.mdx
./docs/sat/docs/installation/terraform/index.mdx
./docs/sat/docs/motivation.mdx
./docs/sat/docs/troubleshooting.mdx
./docs/sat/docs/usage.mdx
./docs/sat/docusaurus.config.ts
./docs/sat/package.json
./docs/sat/sidebars.ts
./docs/sat/src/components/AccordionItem.tsx
./docs/sat/src/components/Button.tsx
./docs/sat/src/css/custom.css
./docs/sat/src/pages/index.tsx
./docs/sat/static/.nojekyll
./docs/sat/static/gif/terminal-aws.gif
./docs/sat/static/gif/terminal-azure.gif
./docs/sat/static/gif/terminal-gcp.gif
./docs/sat/static/img/additional_details_1.png
./docs/sat/static/img/additional_details_2.png
./docs/sat/static/img/alert_destination.png
./docs/sat/static/img/alert_details.png
./docs/sat/static/img/alert_settings.png
./docs/sat/static/img/alerts_view.png
./docs/sat/static/img/aws_ws.png
./docs/sat/static/img/azure_app_reg.png
./docs/sat/static/img/azure_role_assignment.png
./docs/sat/static/img/azure_ws.png
./docs/sat/static/img/catalog_view.png
./docs/sat/static/img/executive_dashboard.png
./docs/sat/static/img/gcp_ws.png
./docs/sat/static/img/logo.svg
./docs/sat/static/img/sat_dashboard_partial.png
./docs/sat/static/img/sat_detection_partial.png
./docs/sat/static/img/sat_functionality.png
./docs/sat/static/img/secret_scanner_dashboard.png
./docs/sat/static/img/security_config_comparison.png
./docs/sat/static/img/security_deviation_trend.png
./docs/sat/static/img/upate_security_best_practices.png
./docs/sat/static/img/update_workspace_configuration.png
./docs/sat/tailwind.config.ts
./docs/sat/tsconfig.json
./docs/sat/yarn.lock
./docs/setup.md
./install.sh
./lib/dbl_sat_sdk-0.1.40-py3-none-any.whl
./notebooks/Includes/install_sat_sdk.py
./notebooks/Includes/scan_secrets/cluster_secrets_scan.py
./notebooks/Includes/scan_secrets/notebook_secret_scan.py
./notebooks/Includes/workspace_analysis.py
./notebooks/Includes/workspace_settings.py
./notebooks/Includes/workspace_stats.py
./notebooks/Setup/1. list_account_workspaces_to_conf_file.py
./notebooks/Setup/3. test_connections.py
./notebooks/Setup/4. enable_workspaces_for_sat.py
./notebooks/Setup/5. import_dashboard_template_lakeview.py
./notebooks/Setup/6. configure_alerts_template.py
./notebooks/Setup/7. update_sat_check_configuration.py
./notebooks/Setup/8. update_workspace_configuration.py
./notebooks/Setup/9. self_assess_workspace_configuration.py
./notebooks/Utils/accounts_bootstrap.py
./notebooks/Utils/common.py
./notebooks/Utils/initialize.py
./notebooks/Utils/sat_checks_config.py
./notebooks/Utils/workspace_bootstrap.py
./notebooks/brickhound/00_analysis_common.py
./notebooks/brickhound/00_config.py
./notebooks/brickhound/01_principal_resource_analysis.py
./notebooks/brickhound/02_escalation_paths.py
./notebooks/brickhound/03_impersonation_analysis.py
./notebooks/brickhound/04_advanced_reports.py
./notebooks/brickhound/README.md
./notebooks/diagnosis/pre_run_config_check.py
./notebooks/diagnosis/sat_diagnosis_aws.py
./notebooks/diagnosis/sat_diagnosis_aws_govcloud.py
./notebooks/diagnosis/sat_diagnosis_azure.py
./notebooks/diagnosis/sat_diagnosis_gcp.py
./notebooks/diagnosis/sat_diagnosis_trufflehog.py
./notebooks/export/export_sat_report.py
./notebooks/permission_analysis_data_collection.py
./notebooks/security_analysis_driver.py
./notebooks/security_analysis_initializer.py
./notebooks/security_analysis_secrets_scanner.py
./src/brickhound/__init__.py
./src/brickhound/cli.py
./src/brickhound/collector/__init__.py
./src/brickhound/collector/core.py
./src/brickhound/graph/__init__.py
./src/brickhound/graph/analyzer.py
./src/brickhound/graph/builder.py
./src/brickhound/graph/permissions_resolver.py
./src/brickhound/graph/schema.py
./src/brickhound/setup.py
./src/brickhound/utils/__init__.py
./src/brickhound/utils/api_client.py
./src/brickhound/utils/config.py
./src/securityanalysistoolproject/.vscode/launch.json
./src/securityanalysistoolproject/README.md
./src/securityanalysistoolproject/clientpkgs/__init__.py
./src/securityanalysistoolproject/clientpkgs/accounts_billing.py
./src/securityanalysistoolproject/clientpkgs/accounts_client.py
./src/securityanalysistoolproject/clientpkgs/accounts_iam.py
./src/securityanalysistoolproject/clientpkgs/accounts_oauth.py
./src/securityanalysistoolproject/clientpkgs/accounts_provisioning_client.py
./src/securityanalysistoolproject/clientpkgs/accounts_settings.py
./src/securityanalysistoolproject/clientpkgs/accounts_uc_client.py
./src/securityanalysistoolproject/clientpkgs/apps_client.py
./src/securityanalysistoolproject/clientpkgs/azure_accounts_client.py
./src/securityanalysistoolproject/clientpkgs/cleanrooms_client.py
./src/securityanalysistoolproject/clientpkgs/clusters_client.py
./src/securityanalysistoolproject/clientpkgs/dbfs_client.py
./src/securityanalysistoolproject/clientpkgs/dbsql_client.py
./src/securityanalysistoolproject/clientpkgs/delta_sharing.py
./src/securityanalysistoolproject/clientpkgs/init_scripts_client.py
./src/securityanalysistoolproject/clientpkgs/ip_access_list.py
./src/securityanalysistoolproject/clientpkgs/job_runs_client.py
./src/securityanalysistoolproject/clientpkgs/jobs_client.py
./src/securityanalysistoolproject/clientpkgs/lakeview_client.py
./src/securityanalysistoolproject/clientpkgs/libraries_client.py
./src/securityanalysistoolproject/clientpkgs/managed_libraries_client.py
./src/securityanalysistoolproject/clientpkgs/marketplace_client.py
./src/securityanalysistoolproject/clientpkgs/ml_flow_client.py
./src/securityanalysistoolproject/clientpkgs/notifications_destination.py
./src/securityanalysistoolproject/clientpkgs/permissions_client.py
./src/securityanalysistoolproject/clientpkgs/pipelines_client.py
./src/securityanalysistoolproject/clientpkgs/policies_client.py
./src/securityanalysistoolproject/clientpkgs/pools_client.py
./src/securityanalysistoolproject/clientpkgs/qualitymonitors_client.py
./src/securityanalysistoolproject/clientpkgs/repos_client.py
./src/securityanalysistoolproject/clientpkgs/scim_client.py
./src/securityanalysistoolproject/clientpkgs/secrets_client.py
./src/securityanalysistoolproject/clientpkgs/serving_endpoints.py
./src/securityanalysistoolproject/clientpkgs/tokens_client.py
./src/securityanalysistoolproject/clientpkgs/unity_catalog_client.py
./src/securityanalysistoolproject/clientpkgs/vector_search.py
./src/securityanalysistoolproject/clientpkgs/workspace_client.py
./src/securityanalysistoolproject/clientpkgs/ws_settings_client.py
./src/securityanalysistoolproject/core/__init__.py
./src/securityanalysistoolproject/core/dbclient.py
./src/securityanalysistoolproject/core/logging_utils.py
./src/securityanalysistoolproject/core/parser.py
./src/securityanalysistoolproject/core/wmconstants.py
./src/securityanalysistoolproject/dist/dbl_sat_sdk-0.0.127-py3-none-any.whl
./src/securityanalysistoolproject/main.py
./src/securityanalysistoolproject/pyproject.toml
./src/securityanalysistoolproject/readmepypi.txt
./src/securityanalysistoolproject/setup.cfg
./src/securityanalysistoolproject/setup.py
./src/securityanalysistoolproject/tests/__init__.py
./src/securityanalysistoolproject/tests/conftest.py
./src/securityanalysistoolproject/tests/readme.txt
./src/securityanalysistoolproject/tests/test_accountclients.py
./src/securityanalysistoolproject/tests/test_accounts_billing.py
./src/securityanalysistoolproject/tests/test_accountsettings.py
```

## Local Directory Structure

```
./.databricks/.gitignore
./.databricks/bundle/dev/deployment.json
./.databricks/bundle/dev/sync-snapshots/d2340b0f33093b87.json
./.databricks/bundle/dev/terraform/.terraform.lock.hcl
./.databricks/bundle/dev/terraform/.terraform/providers/registry.terraform.io/databricks/databricks/1.94.0/darwin_arm64/CHANGELOG.md
./.databricks/bundle/dev/terraform/.terraform/providers/registry.terraform.io/databricks/databricks/1.94.0/darwin_arm64/LICENSE
./.databricks/bundle/dev/terraform/.terraform/providers/registry.terraform.io/databricks/databricks/1.94.0/darwin_arm64/NOTICE
./.databricks/bundle/dev/terraform/.terraform/providers/registry.terraform.io/databricks/databricks/1.94.0/darwin_arm64/terraform-provider-databricks_v1.94.0
./.databricks/bundle/dev/terraform/bundle.tf.json
./.databricks/bundle/dev/terraform/plan
./.databricks/bundle/dev/terraform/terraform.tfstate
./.databricks/bundle/dev/terraform/terraform.tfstate.backup
./README.md
./UPSTREAM_DIFF.md
./configs/sat_dasf_mapping.csv
./configs/security_best_practices.csv
./configs/self_assessment_checks.yaml
./configs/trufflehog_detectors.yaml
./configs/workspace_configs.csv
./dashboards/SAT_Dashboard_definition.json
./databricks.yml
./download_trufflehog.sh
./download_wheels.sh
./notebooks/Includes/install_sat_sdk.py
./notebooks/Includes/install_sat_sdk.py.bak
./notebooks/Includes/scan_secrets/cluster_secrets_scan.py
./notebooks/Includes/scan_secrets/notebook_secret_scan.py
./notebooks/Includes/workspace_analysis.py
./notebooks/Includes/workspace_settings.py
./notebooks/Includes/workspace_stats.py
./notebooks/Setup/1. list_account_workspaces_to_conf_file.py
./notebooks/Setup/3. test_connections.py
./notebooks/Setup/4. enable_workspaces_for_sat.py
./notebooks/Setup/5. import_dashboard_template_lakeview.py
./notebooks/Setup/6. configure_alerts_template.py
./notebooks/Setup/7. update_sat_check_configuration.py
./notebooks/Setup/8. update_workspace_configuration.py
./notebooks/Setup/9. self_assess_workspace_configuration.py
./notebooks/Utils/accounts_bootstrap.py
./notebooks/Utils/common.py
./notebooks/Utils/initialize.py
./notebooks/Utils/sat_checks_config.py
./notebooks/Utils/workspace_bootstrap.py
./notebooks/brickhound/00_analysis_common.py
./notebooks/brickhound/00_config.py
./notebooks/brickhound/01_principal_resource_analysis.py
./notebooks/brickhound/02_escalation_paths.py
./notebooks/brickhound/03_impersonation_analysis.py
./notebooks/brickhound/04_advanced_reports.py
./notebooks/brickhound/README.md
./notebooks/diagnosis/pre_run_config_check.py
./notebooks/diagnosis/sat_diagnosis_aws.py
./notebooks/diagnosis/sat_diagnosis_aws_govcloud.py
./notebooks/diagnosis/sat_diagnosis_azure.py
./notebooks/diagnosis/sat_diagnosis_gcp.py
./notebooks/diagnosis/sat_diagnosis_trufflehog.py
./notebooks/export/export_sat_report.py
./notebooks/permission_analysis_data_collection.py
./notebooks/security_analysis_driver.py
./notebooks/security_analysis_initializer.py
./notebooks/security_analysis_secrets_scanner.py
./resources/sat_driver_job.yml
./resources/sat_initializer_job.yml
./resources/sat_secrets_scanner_job.yml
./setup_workspaces.py
```

---

## File Comparison

### Files only in local (added/customized)

```
./.databricks/.gitignore
./.databricks/bundle/dev/deployment.json
./.databricks/bundle/dev/sync-snapshots/d2340b0f33093b87.json
./.databricks/bundle/dev/terraform/.terraform.lock.hcl
./.databricks/bundle/dev/terraform/.terraform/providers/registry.terraform.io/databricks/databricks/1.94.0/darwin_arm64/CHANGELOG.md
./.databricks/bundle/dev/terraform/.terraform/providers/registry.terraform.io/databricks/databricks/1.94.0/darwin_arm64/LICENSE
./.databricks/bundle/dev/terraform/.terraform/providers/registry.terraform.io/databricks/databricks/1.94.0/darwin_arm64/NOTICE
./.databricks/bundle/dev/terraform/.terraform/providers/registry.terraform.io/databricks/databricks/1.94.0/darwin_arm64/terraform-provider-databricks_v1.94.0
./.databricks/bundle/dev/terraform/bundle.tf.json
./.databricks/bundle/dev/terraform/plan
./.databricks/bundle/dev/terraform/terraform.tfstate
./.databricks/bundle/dev/terraform/terraform.tfstate.backup
./UPSTREAM_DIFF.md
./configs/workspace_configs.csv
./databricks.yml
./download_trufflehog.sh
./download_wheels.sh
./notebooks/Includes/install_sat_sdk.py.bak
./resources/sat_driver_job.yml
./resources/sat_initializer_job.yml
./resources/sat_secrets_scanner_job.yml
./setup_workspaces.py
```

### Files only in upstream (not included locally)

```
./.github/ISSUE_TEMPLATE/bug_report.yml
./.github/ISSUE_TEMPLATE/config.yml
./.github/ISSUE_TEMPLATE/doc_request.yml
./.github/ISSUE_TEMPLATE/feature_request.yml
./.github/ISSUE_TEMPLATE/general_issue.md
./.github/pull_request_template.md
./.github/workflows/security-scan.yml
./.gitignore
./CHANGELOG.md
./CONTRIBUTING.md
./LICENSE
./NOTICE
./SECURITY.md
./VERSIONING.md
./app/brickhound/README.md
./app/brickhound/app.py
./app/brickhound/app.yaml
./app/brickhound/databricks.yml
./app/brickhound/requirements.txt
./dabs/dabs_template/databricks_template_schema.json
./dabs/dabs_template/template/tmp/databricks.yml.tmpl
./dabs/dabs_template/template/tmp/resources/brickhound_job.yml.tmpl
./dabs/dabs_template/template/tmp/resources/sat_driver_job.yml.tmpl
./dabs/dabs_template/template/tmp/resources/sat_initiliazer_job.yml.tmpl
./dabs/dabs_template/template/tmp/resources/sat_secrets_scanner_job.yml.tmpl
./dabs/main.py
./dabs/requirements.txt
./dabs/sat/__init__.py
./dabs/sat/config.py
./dabs/sat/utils.py
./dabs/setup.sh
./docs/.gitignore
./docs/sat/.gitignore
./docs/sat/docs/faq.mdx
./docs/sat/docs/functionality.mdx
./docs/sat/docs/installation/index.mdx
./docs/sat/docs/installation/standard/aws.mdx
./docs/sat/docs/installation/standard/azure.mdx
./docs/sat/docs/installation/standard/gcp.mdx
./docs/sat/docs/installation/standard/index.mdx
./docs/sat/docs/installation/terraform/aws.mdx
./docs/sat/docs/installation/terraform/azure.mdx
./docs/sat/docs/installation/terraform/gcp.mdx
./docs/sat/docs/installation/terraform/index.mdx
./docs/sat/docs/motivation.mdx
./docs/sat/docs/troubleshooting.mdx
./docs/sat/docs/usage.mdx
./docs/sat/docusaurus.config.ts
./docs/sat/package.json
./docs/sat/sidebars.ts
./docs/sat/src/components/AccordionItem.tsx
./docs/sat/src/components/Button.tsx
./docs/sat/src/css/custom.css
./docs/sat/src/pages/index.tsx
./docs/sat/static/.nojekyll
./docs/sat/static/gif/terminal-aws.gif
./docs/sat/static/gif/terminal-azure.gif
./docs/sat/static/gif/terminal-gcp.gif
./docs/sat/static/img/additional_details_1.png
./docs/sat/static/img/additional_details_2.png
./docs/sat/static/img/alert_destination.png
./docs/sat/static/img/alert_details.png
./docs/sat/static/img/alert_settings.png
./docs/sat/static/img/alerts_view.png
./docs/sat/static/img/aws_ws.png
./docs/sat/static/img/azure_app_reg.png
./docs/sat/static/img/azure_role_assignment.png
./docs/sat/static/img/azure_ws.png
./docs/sat/static/img/catalog_view.png
./docs/sat/static/img/executive_dashboard.png
./docs/sat/static/img/gcp_ws.png
./docs/sat/static/img/logo.svg
./docs/sat/static/img/sat_dashboard_partial.png
./docs/sat/static/img/sat_detection_partial.png
./docs/sat/static/img/sat_functionality.png
./docs/sat/static/img/secret_scanner_dashboard.png
./docs/sat/static/img/security_config_comparison.png
./docs/sat/static/img/security_deviation_trend.png
./docs/sat/static/img/upate_security_best_practices.png
./docs/sat/static/img/update_workspace_configuration.png
./docs/sat/tailwind.config.ts
./docs/sat/tsconfig.json
./docs/sat/yarn.lock
./docs/setup.md
./install.sh
./lib/dbl_sat_sdk-0.1.40-py3-none-any.whl
./src/brickhound/__init__.py
./src/brickhound/cli.py
./src/brickhound/collector/__init__.py
./src/brickhound/collector/core.py
./src/brickhound/graph/__init__.py
./src/brickhound/graph/analyzer.py
./src/brickhound/graph/builder.py
./src/brickhound/graph/permissions_resolver.py
./src/brickhound/graph/schema.py
./src/brickhound/setup.py
./src/brickhound/utils/__init__.py
./src/brickhound/utils/api_client.py
./src/brickhound/utils/config.py
./src/securityanalysistoolproject/.vscode/launch.json
./src/securityanalysistoolproject/README.md
./src/securityanalysistoolproject/clientpkgs/__init__.py
./src/securityanalysistoolproject/clientpkgs/accounts_billing.py
./src/securityanalysistoolproject/clientpkgs/accounts_client.py
./src/securityanalysistoolproject/clientpkgs/accounts_iam.py
./src/securityanalysistoolproject/clientpkgs/accounts_oauth.py
./src/securityanalysistoolproject/clientpkgs/accounts_provisioning_client.py
./src/securityanalysistoolproject/clientpkgs/accounts_settings.py
./src/securityanalysistoolproject/clientpkgs/accounts_uc_client.py
./src/securityanalysistoolproject/clientpkgs/apps_client.py
./src/securityanalysistoolproject/clientpkgs/azure_accounts_client.py
./src/securityanalysistoolproject/clientpkgs/cleanrooms_client.py
./src/securityanalysistoolproject/clientpkgs/clusters_client.py
./src/securityanalysistoolproject/clientpkgs/dbfs_client.py
./src/securityanalysistoolproject/clientpkgs/dbsql_client.py
./src/securityanalysistoolproject/clientpkgs/delta_sharing.py
./src/securityanalysistoolproject/clientpkgs/init_scripts_client.py
./src/securityanalysistoolproject/clientpkgs/ip_access_list.py
./src/securityanalysistoolproject/clientpkgs/job_runs_client.py
./src/securityanalysistoolproject/clientpkgs/jobs_client.py
./src/securityanalysistoolproject/clientpkgs/lakeview_client.py
./src/securityanalysistoolproject/clientpkgs/libraries_client.py
./src/securityanalysistoolproject/clientpkgs/managed_libraries_client.py
./src/securityanalysistoolproject/clientpkgs/marketplace_client.py
./src/securityanalysistoolproject/clientpkgs/ml_flow_client.py
./src/securityanalysistoolproject/clientpkgs/notifications_destination.py
./src/securityanalysistoolproject/clientpkgs/permissions_client.py
./src/securityanalysistoolproject/clientpkgs/pipelines_client.py
./src/securityanalysistoolproject/clientpkgs/policies_client.py
./src/securityanalysistoolproject/clientpkgs/pools_client.py
./src/securityanalysistoolproject/clientpkgs/qualitymonitors_client.py
./src/securityanalysistoolproject/clientpkgs/repos_client.py
./src/securityanalysistoolproject/clientpkgs/scim_client.py
./src/securityanalysistoolproject/clientpkgs/secrets_client.py
./src/securityanalysistoolproject/clientpkgs/serving_endpoints.py
./src/securityanalysistoolproject/clientpkgs/tokens_client.py
./src/securityanalysistoolproject/clientpkgs/unity_catalog_client.py
./src/securityanalysistoolproject/clientpkgs/vector_search.py
./src/securityanalysistoolproject/clientpkgs/workspace_client.py
./src/securityanalysistoolproject/clientpkgs/ws_settings_client.py
./src/securityanalysistoolproject/core/__init__.py
./src/securityanalysistoolproject/core/dbclient.py
./src/securityanalysistoolproject/core/logging_utils.py
./src/securityanalysistoolproject/core/parser.py
./src/securityanalysistoolproject/core/wmconstants.py
./src/securityanalysistoolproject/dist/dbl_sat_sdk-0.0.127-py3-none-any.whl
./src/securityanalysistoolproject/main.py
./src/securityanalysistoolproject/pyproject.toml
./src/securityanalysistoolproject/readmepypi.txt
./src/securityanalysistoolproject/setup.cfg
./src/securityanalysistoolproject/setup.py
./src/securityanalysistoolproject/tests/__init__.py
./src/securityanalysistoolproject/tests/conftest.py
./src/securityanalysistoolproject/tests/readme.txt
./src/securityanalysistoolproject/tests/test_accountclients.py
./src/securityanalysistoolproject/tests/test_accounts_billing.py
./src/securityanalysistoolproject/tests/test_accountsettings.py
./src/securityanalysistoolproject/tests/test_apps.py
./src/securityanalysistoolproject/tests/test_cleanrooms.py
./src/securityanalysistoolproject/tests/test_clusters.py
./src/securityanalysistoolproject/tests/test_connection.py
./src/securityanalysistoolproject/tests/test_dbfs.py
./src/securityanalysistoolproject/tests/test_dbsql.py
./src/securityanalysistoolproject/tests/test_deltasharing.py
./src/securityanalysistoolproject/tests/test_funcs1.py
./src/securityanalysistoolproject/tests/test_initscripts.py
./src/securityanalysistoolproject/tests/test_ipaccess.py
./src/securityanalysistoolproject/tests/test_jobs.py
./src/securityanalysistoolproject/tests/test_lakeview.py
./src/securityanalysistoolproject/tests/test_local.py
./src/securityanalysistoolproject/tests/test_logs.py
./src/securityanalysistoolproject/tests/test_managed_libraries.py
./src/securityanalysistoolproject/tests/test_marketplace.py
./src/securityanalysistoolproject/tests/test_mlflow.py
./src/securityanalysistoolproject/tests/test_oauth.py
./src/securityanalysistoolproject/tests/test_permissions.py
./src/securityanalysistoolproject/tests/test_pipelines.py
./src/securityanalysistoolproject/tests/test_policies.py
./src/securityanalysistoolproject/tests/test_qualitymonitors.py
./src/securityanalysistoolproject/tests/test_repos.py
./src/securityanalysistoolproject/tests/test_scim.py
./src/securityanalysistoolproject/tests/test_secrets.py
./src/securityanalysistoolproject/tests/test_servingendpoints.py
./src/securityanalysistoolproject/tests/test_tokens.py
./src/securityanalysistoolproject/tests/test_uc.py
./src/securityanalysistoolproject/tests/test_unitycatalog.py
./src/securityanalysistoolproject/tests/test_vectorsearch.py
./src/securityanalysistoolproject/tests/test_workspace.py
./src/securityanalysistoolproject/tests/test_wssettings.py
./terraform/aws/TERRAFORM_AWS.md
./terraform/aws/provider.tf
./terraform/aws/secrets.tf
./terraform/aws/template.tfvars
./terraform/aws/variables.tf
./terraform/azure/TERRAFORM_Azure.md
./terraform/azure/provider.tf
./terraform/azure/secrets.tf
./terraform/azure/service_principal.tf
./terraform/azure/template.tfvars
./terraform/azure/variables.tf
./terraform/common/brickhound_app.tf
./terraform/common/brickhound_job.tf
./terraform/common/data.tf
./terraform/common/jobs.tf
./terraform/common/outputs.tf
./terraform/common/provider.tf
./terraform/common/repo.tf
./terraform/common/secrets.tf
./terraform/common/sql_warehouse.tf
./terraform/common/variables.tf
./terraform/gcp/TERRAFORM_GCP.md
./terraform/gcp/provider.tf
./terraform/gcp/secrets.tf
./terraform/gcp/template.tfvars
./terraform/gcp/variables.tf
```

### Files in both (may have modifications)

```
./README.md
./configs/sat_dasf_mapping.csv
./configs/security_best_practices.csv
./configs/self_assessment_checks.yaml
./configs/trufflehog_detectors.yaml
./dashboards/SAT_Dashboard_definition.json
./notebooks/Includes/install_sat_sdk.py
./notebooks/Includes/scan_secrets/cluster_secrets_scan.py
./notebooks/Includes/scan_secrets/notebook_secret_scan.py
./notebooks/Includes/workspace_analysis.py
./notebooks/Includes/workspace_settings.py
./notebooks/Includes/workspace_stats.py
./notebooks/Setup/1. list_account_workspaces_to_conf_file.py
./notebooks/Setup/3. test_connections.py
./notebooks/Setup/4. enable_workspaces_for_sat.py
./notebooks/Setup/5. import_dashboard_template_lakeview.py
./notebooks/Setup/6. configure_alerts_template.py
./notebooks/Setup/7. update_sat_check_configuration.py
./notebooks/Setup/8. update_workspace_configuration.py
./notebooks/Setup/9. self_assess_workspace_configuration.py
./notebooks/Utils/accounts_bootstrap.py
./notebooks/Utils/common.py
./notebooks/Utils/initialize.py
./notebooks/Utils/sat_checks_config.py
./notebooks/Utils/workspace_bootstrap.py
./notebooks/brickhound/00_analysis_common.py
./notebooks/brickhound/00_config.py
./notebooks/brickhound/01_principal_resource_analysis.py
./notebooks/brickhound/02_escalation_paths.py
./notebooks/brickhound/03_impersonation_analysis.py
./notebooks/brickhound/04_advanced_reports.py
./notebooks/brickhound/README.md
./notebooks/diagnosis/pre_run_config_check.py
./notebooks/diagnosis/sat_diagnosis_aws.py
./notebooks/diagnosis/sat_diagnosis_aws_govcloud.py
./notebooks/diagnosis/sat_diagnosis_azure.py
./notebooks/diagnosis/sat_diagnosis_gcp.py
./notebooks/diagnosis/sat_diagnosis_trufflehog.py
./notebooks/export/export_sat_report.py
./notebooks/permission_analysis_data_collection.py
./notebooks/security_analysis_driver.py
./notebooks/security_analysis_initializer.py
./notebooks/security_analysis_secrets_scanner.py
```

---

## Detailed Diffs for Common Files

### `./README.md`

```diff
--- /var/folders/k7/vpv8ffjj5cbf6xhyk6v9xshh0000gn/T/tmp.SwRqtTEdRs/security-analysis-tool/./README.md	2026-02-18 23:40:42
+++ /Users/fredrik/src/origo/padda-golden-path/bundles/sat-tool/./README.md	2026-02-18 16:53:19
@@ -1,37 +1,77 @@
-# SAT: Monitor the Security Health of Databricks Workspaces
+# SAT — Databricks Asset Bundle (isolated VPC, serverless)
 
-The **Security Analysis Tool (SAT)** analyzes your Databricks account and workspace configurations, providing recommendations to help you follow Databricks' security best practices.
+Single-workspace serverless deployment of the Databricks Security Analysis Tool.
+No internet access needed in the workspace — wheels, TruffleHog binary, and
+workspace configs are all bundled and deployed together.
 
-## BrickHound Permissions Analysis
+## Architecture
 
-SAT now includes **BrickHound**, a graph-based permissions analysis tool that complements SAT's configuration security checks:
+```
+Your machine (has internet + account API access)
+  ├── setup_workspaces.py   → calls Accounts API, generates workspace_configs.csv
+  ├── download_wheels.sh    → downloads Python wheels for the SAT SDK
+  ├── download_trufflehog.sh→ downloads TruffleHog binary (Linux x86_64)
+  └── databricks bundle deploy → pushes everything to the workspace
 
-- **Interactive Notebooks**: Query permissions across your Databricks account
-- **Web UI**: User-friendly interface for permissions exploration
-- **Graph Analysis**: Find privilege escalation paths and impersonation risks
-- **Compliance Reports**: Generate access audit reports
+Workspace (SRA isolated, no internet)
+  ├── sat_initializer job   → one-time: loads config into tables, imports dashboard
+  ├── sat_driver job        → scheduled: runs security analysis
+  └── sat_secrets_scanner   → scheduled: scans notebooks/clusters for secrets
+```
 
-**Get Started:**
-1. Run the BrickHound data collection job: Workflows → Jobs → "BrickHound Permissions Analysis"
-2. Use analysis notebooks in `/notebooks/brickhound/`
-3. Or access the web UI at `https://<workspace-url>/apps/brickhound-sat`
+- **padda-iac** `tf/modules/sat/`: Secrets, SQL warehouse, Service Principal
+- **This DAB**: Notebooks, wheels, TruffleHog binary, serverless job definitions
 
-**Documentation**: [BrickHound Integration Guide](docs/BRICKHOUND_INTEGRATION.md)
+## Setup
 
-## Documentation
+### 1. Prerequisites
 
-Refer to the [SAT documentation](https://databricks-industry-solutions.github.io/security-analysis-tool/) for detailed information on how to use SAT, its features, and configuration options.
+```bash
+pip install databricks-sdk
+databricks auth login --account-id <ACCOUNT_ID>
+```
 
-## Project Support
+### 2. Configure workspaces (runs locally, calls Accounts API)
 
-The code in this project is provided **for exploration purposes only** and is **not formally supported** by Databricks under any Service Level Agreements (SLAs). It is provided **AS-IS**, without any warranties or guarantees.  
+```bash
+# All running workspaces in the account:
+python setup_workspaces.py --account-id <ACCOUNT_ID>
 
-Please **do not submit support tickets** to Databricks for issues related to the use of this project.  
+# Specific workspaces only:
+python setup_workspaces.py --account-id <ACCOUNT_ID> \
+    --workspace-ids 2727440053493594 1234567890123456
 
-The source code provided is subject to the Databricks [LICENSE](https://github.com/databricks-industry-solutions/security-analysis-tool/blob/main/LICENSE) . All third-party libraries included or referenced are subject to their respective licenses set forth in the project license.  
+# Skip connection tests:
+python setup_workspaces.py --account-id <ACCOUNT_ID> --skip-connection-test
+```
 
-Any issues or bugs found should be submitted as **GitHub Issues** on the project repository. While these will be reviewed as time permits, there are **no formal SLAs** for support.
+This generates `configs/workspace_configs.csv`.
 
-## Contributing
+### 3. Download dependencies (runs locally, needs internet)
 
-We happily welcome contributions. We accept PRs pursuant to a CLA.
+```bash
+./download_wheels.sh
+./download_trufflehog.sh
+```
+
+### 4. Deploy + initialize
+
+```bash
+databricks bundle deploy --target dev
+databricks bundle run sat_initializer --target dev
+```
+
+### 5. Done
+
+The driver (Mon/Wed/Fri 07:00 Oslo) and secrets scanner (daily 08:00 Oslo)
+run on schedule. No further internet or account API access needed.
+
+## Adding a new workspace
+
+Re-run `setup_workspaces.py` and redeploy:
+
+```bash
+python setup_workspaces.py --account-id <ACCOUNT_ID>
+databricks bundle deploy --target dev
... (     102 total lines, truncated)
```

### `./notebooks/Includes/install_sat_sdk.py`

```diff
--- /var/folders/k7/vpv8ffjj5cbf6xhyk6v9xshh0000gn/T/tmp.SwRqtTEdRs/security-analysis-tool/./notebooks/Includes/install_sat_sdk.py	2026-02-18 23:40:42
+++ /Users/fredrik/src/origo/padda-golden-path/bundles/sat-tool/./notebooks/Includes/install_sat_sdk.py	2026-02-18 17:08:53
@@ -1,55 +1,93 @@
 # Databricks notebook source
 # MAGIC %md
-# MAGIC **Notebook name:** install_sat_sdk  
-# MAGIC **Functionality:** Installs the necessary sat sdk
+# MAGIC **Notebook name:** install_sat_sdk
+# MAGIC **Functionality:** Installs the necessary sat sdk (isolated VPC — wheels bundled via DAB)
 
 # COMMAND ----------
 
-RECOMMENDED_DBR_FOR_SAT= 14.3
+RECOMMENDED_DBR_FOR_SAT = 14.3
 import os
-#Get databricks runtime configured to run SAT
-dbr_version = os.environ.get('DATABRICKS_RUNTIME_VERSION','0.0')
+
+# Get databricks runtime configured to run SAT
+dbr_version = os.environ.get("DATABRICKS_RUNTIME_VERSION", "0.0")
 is_sat_compatible = False
-is_serverless= False
-#sanity check in case there is major and minor version
-#strip minor version since we need to compare as number
-if(dbr_version.startswith("client")):
+is_serverless = False
+# sanity check in case there is major and minor version
+# strip minor version since we need to compare as number
+if dbr_version.startswith("client"):
     is_sat_compatible = True
     is_serverless = True
 else:
-    dbrarray = dbr_version.split('.')
-    dbr_version =  f'{dbrarray[0]}.{dbrarray[1]}'
+    dbrarray = dbr_version.split(".")
+    dbr_version = f"{dbrarray[0]}.{dbrarray[1]}"
     dbr_version = float(dbr_version)
     is_sat_compatible = True if dbr_version >= RECOMMENDED_DBR_FOR_SAT else False
 
-#test version
+# test version
 
-if is_sat_compatible== False:
-    dbutils.notebook.exit(f"Detected DBR version {dbr_version} . Please use the DBR {RECOMMENDED_DBR_FOR_SAT} for SAT and try again , please refer to docs/setup.md")
+if is_sat_compatible == False:
+    dbutils.notebook.exit(
+        f"Detected DBR version {dbr_version} . Please use the DBR {RECOMMENDED_DBR_FOR_SAT} for SAT and try again , please refer to docs/setup.md"
+    )
 
 # COMMAND ----------
 
-SDK_VERSION='0.1.40'
+SDK_VERSION = "0.1.38"
 
 # COMMAND ----------
 
-def getLibPath():
-    path = (
-        dbutils.notebook.entry_point.getDbutils()
-        .notebook()
-        .getContext()
-        .notebookPath()
-        .get()
-    )
-    path = path[: path.find("/notebooks")]
-    return f"/Workspace{path}/lib"
+# Wheels are synced to the workspace by the DAB deploy.
+# Install from the bundle's wheels directory — no PyPI needed.
+# Derive the wheels path relative to this notebook's location.
+import subprocess
+import sys
 
-# COMMAND ----------
+notebook_path = (
+    dbutils.notebook.entry_point.getDbutils()
+    .notebook()
+    .getContext()
+    .notebookPath()
+    .get()
+)
+# notebook_path may or may not include the /Workspace prefix depending on
+# the runtime (serverless vs classic) and deployment target (dev vs prod).
+# Ensure it always starts with /Workspace so pip can resolve the local path.
+bundle_root = notebook_path.rsplit("/notebooks/", 1)[0]
+if not bundle_root.startswith("/Workspace"):
+    bundle_root = f"/Workspace{bundle_root}"
+wheels_path = f"{bundle_root}/wheels"
 
-# Construct workspace path to wheel file dynamically
-WHEEL_PATH = f'{getLibPath()}/dbl_sat_sdk-{SDK_VERSION}-py3-none-any.whl'
-print(f"Installing SAT SDK from: {WHEEL_PATH}")
+import glob
 
-# COMMAND ----------
+# Filter wheels to only those compatible with the running Python.
+# We bundle wheels for multiple cpython versions (cp311–cp314); installing
+# the wrong one causes pip to fail, so pick only matching or universal wheels.
+py_ver = f"cp{sys.version_info.major}{sys.version_info.minor}"
+print(f"Python: {sys.version} (tag: {py_ver})")
 
... (     127 total lines, truncated)
```

### `./notebooks/Includes/scan_secrets/cluster_secrets_scan.py`

```diff
--- /var/folders/k7/vpv8ffjj5cbf6xhyk6v9xshh0000gn/T/tmp.SwRqtTEdRs/security-analysis-tool/./notebooks/Includes/scan_secrets/cluster_secrets_scan.py	2026-02-18 23:40:42
+++ /Users/fredrik/src/origo/padda-golden-path/bundles/sat-tool/./notebooks/Includes/scan_secrets/cluster_secrets_scan.py	2026-02-18 21:23:55
@@ -95,53 +95,28 @@
 
 # COMMAND ----------
 
-# MAGIC %sh
-# MAGIC # Install required Python packages
-# MAGIC pip install requests pyyaml
-# MAGIC
-# MAGIC # Check if TruffleHog is already installed (likely from notebook scanner)
-# MAGIC if [ -f /tmp/trufflehog ]; then
-# MAGIC     echo "TruffleHog already installed at /tmp/trufflehog"
-# MAGIC     echo "Skipping installation (reusing from notebook scanner)"
-# MAGIC else
-# MAGIC     # Download and install TruffleHog binary to /tmp directory
-# MAGIC     echo "Installing TruffleHog..."
-# MAGIC     if curl -sSfL https://raw.githubusercontent.com/trufflesecurity/trufflehog/main/scripts/install.sh | sh -s -- -b /tmp; then
-# MAGIC         if [ -f /tmp/trufflehog ]; then
-# MAGIC             echo "Setup completed successfully!"
-# MAGIC             echo "TruffleHog binary location: /tmp/trufflehog"
-# MAGIC         else
-# MAGIC             echo "ERROR: TruffleHog binary not found after installation!"
-# MAGIC             echo "Please verify network access and try again."
-# MAGIC             exit 1
-# MAGIC         fi
-# MAGIC     else
-# MAGIC         echo "=========================================="
-# MAGIC         echo "ERROR: Failed to download TruffleHog"
-# MAGIC         echo "=========================================="
-# MAGIC         echo ""
-# MAGIC         echo "The TruffleHog security scanner could not be downloaded from:"
-# MAGIC         echo "https://raw.githubusercontent.com/trufflesecurity/trufflehog/main/scripts/install.sh"
-# MAGIC         echo ""
-# MAGIC         echo "Possible causes:"
-# MAGIC         echo "  1. Network connectivity issues"
-# MAGIC         echo "  2. Firewall or proxy blocking external downloads"
-# MAGIC         echo "  3. GitHub.com access is restricted in your environment"
-# MAGIC         echo ""
-# MAGIC         echo "ACTION REQUIRED:"
-# MAGIC         echo "Please contact your IT/Security team to allowlist access to:"
-# MAGIC         echo "  - raw.githubusercontent.com"
-# MAGIC         echo "  - github.com/trufflesecurity"
-# MAGIC         echo ""
-# MAGIC         echo "Alternatively, you may need to configure a proxy or use an"
-# MAGIC         echo "internal mirror of the TruffleHog installation package."
-# MAGIC         echo "=========================================="
-# MAGIC         exit 1
-# MAGIC     fi
-# MAGIC fi
-# MAGIC
-# MAGIC echo "✅ TruffleHog setup verified!"
+# Copy bundled TruffleHog binary to /tmp (requests & pyyaml come from bundled wheels via install_sat_sdk)
+import subprocess, sys, shutil, os, stat
 
+if not os.path.exists("/tmp/trufflehog"):
+    # Derive bundle root from notebook path (same pattern as install_sat_sdk)
+    notebook_path = (
+        dbutils.notebook.entry_point.getDbutils()
+        .notebook().getContext().notebookPath().get()
+    )
+    bundle_root = notebook_path.rsplit("/notebooks/", 1)[0]
+    if not bundle_root.startswith("/Workspace"):
+        bundle_root = f"/Workspace{bundle_root}"
+    src = f"{bundle_root}/bin/trufflehog"
+    shutil.copy2(src, "/tmp/trufflehog")
+    os.chmod("/tmp/trufflehog", os.stat("/tmp/trufflehog").st_mode | stat.S_IEXEC)
+    print(f"TruffleHog copied from bundle: {src} -> /tmp/trufflehog")
+else:
+    print("TruffleHog already installed at /tmp/trufflehog")
+
+subprocess.check_call(["/tmp/trufflehog", "--version"])
+print("TruffleHog setup verified!")
+
 # COMMAND ----------
 
 # MAGIC %md
```

### `./notebooks/Includes/scan_secrets/notebook_secret_scan.py`

```diff
--- /var/folders/k7/vpv8ffjj5cbf6xhyk6v9xshh0000gn/T/tmp.SwRqtTEdRs/security-analysis-tool/./notebooks/Includes/scan_secrets/notebook_secret_scan.py	2026-02-18 23:40:42
+++ /Users/fredrik/src/origo/padda-golden-path/bundles/sat-tool/./notebooks/Includes/scan_secrets/notebook_secret_scan.py	2026-02-18 21:23:51
@@ -99,54 +99,28 @@
 
 # COMMAND ----------
 
-# MAGIC %sh
-# MAGIC # Install required Python packages
-# MAGIC pip install requests pyyaml
-# MAGIC
-# MAGIC # Check if TruffleHog is already installed (idempotent installation)
-# MAGIC if [ -f /tmp/trufflehog ]; then
-# MAGIC     echo "TruffleHog already installed at /tmp/trufflehog"
-# MAGIC     echo "Skipping installation (already exists)"
-# MAGIC else
-# MAGIC     # Download and install TruffleHog binary to /tmp directory
-# MAGIC     echo "Installing TruffleHog..."
-# MAGIC     if curl -sSfL https://raw.githubusercontent.com/trufflesecurity/trufflehog/main/scripts/install.sh | sh -s -- -b /tmp; then
-# MAGIC         if [ -f /tmp/trufflehog ]; then
-# MAGIC             echo "Setup completed successfully!"
-# MAGIC             echo "TruffleHog binary location: /tmp/trufflehog"
-# MAGIC             echo "Configuration will be loaded from: /Workspace/Repos/.../configs/trufflehog_detectors.yaml"
-# MAGIC         else
-# MAGIC             echo "ERROR: TruffleHog binary not found after installation!"
-# MAGIC             echo "Please verify network access and try again."
-# MAGIC             exit 1
-# MAGIC         fi
-# MAGIC     else
-# MAGIC         echo "=========================================="
-# MAGIC         echo "ERROR: Failed to download TruffleHog"
-# MAGIC         echo "=========================================="
-# MAGIC         echo ""
-# MAGIC         echo "The TruffleHog security scanner could not be downloaded from:"
-# MAGIC         echo "https://raw.githubusercontent.com/trufflesecurity/trufflehog/main/scripts/install.sh"
-# MAGIC         echo ""
-# MAGIC         echo "Possible causes:"
-# MAGIC         echo "  1. Network connectivity issues"
-# MAGIC         echo "  2. Firewall or proxy blocking external downloads"
-# MAGIC         echo "  3. GitHub.com access is restricted in your environment"
-# MAGIC         echo ""
-# MAGIC         echo "ACTION REQUIRED:"
-# MAGIC         echo "Please contact your IT/Security team to allowlist access to:"
-# MAGIC         echo "  - raw.githubusercontent.com"
-# MAGIC         echo "  - github.com/trufflesecurity"
-# MAGIC         echo ""
-# MAGIC         echo "Alternatively, you may need to configure a proxy or use an"
-# MAGIC         echo "internal mirror of the TruffleHog installation package."
-# MAGIC         echo "=========================================="
-# MAGIC         exit 1
-# MAGIC     fi
-# MAGIC fi
-# MAGIC
-# MAGIC echo "✅ TruffleHog setup verified!"
+# Copy bundled TruffleHog binary to /tmp (requests & pyyaml come from bundled wheels via install_sat_sdk)
+import subprocess, sys, shutil, os, stat
 
+if not os.path.exists("/tmp/trufflehog"):
+    # Derive bundle root from notebook path (same pattern as install_sat_sdk)
+    notebook_path = (
+        dbutils.notebook.entry_point.getDbutils()
+        .notebook().getContext().notebookPath().get()
+    )
+    bundle_root = notebook_path.rsplit("/notebooks/", 1)[0]
+    if not bundle_root.startswith("/Workspace"):
+        bundle_root = f"/Workspace{bundle_root}"
+    src = f"{bundle_root}/bin/trufflehog"
+    shutil.copy2(src, "/tmp/trufflehog")
+    os.chmod("/tmp/trufflehog", os.stat("/tmp/trufflehog").st_mode | stat.S_IEXEC)
+    print(f"TruffleHog copied from bundle: {src} -> /tmp/trufflehog")
+else:
+    print("TruffleHog already installed at /tmp/trufflehog")
+
+subprocess.check_call(["/tmp/trufflehog", "--version"])
+print("TruffleHog setup verified!")
+
 # COMMAND ----------
 
 # MAGIC %md
```

### `./notebooks/Setup/5. import_dashboard_template_lakeview.py`

```diff
--- /var/folders/k7/vpv8ffjj5cbf6xhyk6v9xshh0000gn/T/tmp.SwRqtTEdRs/security-analysis-tool/./notebooks/Setup/5. import_dashboard_template_lakeview.py	2026-02-18 23:40:42
+++ /Users/fredrik/src/origo/padda-golden-path/bundles/sat-tool/./notebooks/Setup/5. import_dashboard_template_lakeview.py	2026-02-18 21:56:39
@@ -69,33 +69,46 @@
     json_.update({'token':token})
 
 db_client = SatDBClient(json_)
-token = db_client.get_temporary_oauth_token()
+oauth_token = db_client.get_temporary_oauth_token()
 
+# Prefer the notebook's native token (job runner identity) over the OAuth token
+# from SatDBClient, since the OAuth token may have limited scope and can't see
+# all warehouses/resources owned by the SP.
+native_token = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().getOrElse(None)
+token = native_token if native_token else oauth_token
+print(f"Using {'native notebook' if native_token else 'OAuth'} token for API calls")
 
 
 
+
 # COMMAND ----------
 
 import requests
 
 DOMAIN = ws.deployment_url
+
 response = requests.get(
           'https://%s/api/2.0/sql/warehouses' % (DOMAIN),
           headers={'Authorization': 'Bearer %s' % token},
           json=None,
-          timeout=60 
+          timeout=60
         )
-        
+
 if response.status_code == 200:
     resources = json.loads(response.text)
     found = False
-    for warehouse in resources["warehouses"]:
+    available_warehouses = [(w['id'], w['name'], w.get('state', 'UNKNOWN')) for w in resources.get("warehouses", [])]
+    print(f"Looking for warehouse ID: {json_['sql_warehouse_id']}")
+    print(f"Available warehouses: {available_warehouses}")
+    for warehouse in resources.get("warehouses", []):
         if warehouse["id"] == json_['sql_warehouse_id']:
             data_source_id = warehouse['id']
             found = True
             break
-    else:
-        dbutils.notebook.exit("The configured SQL Warehouse is not found.")            
+    if not found:
+        dbutils.notebook.exit(f"The configured SQL Warehouse is not found. Looking for: {json_['sql_warehouse_id']}. Available: {available_warehouses}")
+else:
+    print(f"Failed to list warehouses: {response.status_code} {response.text}")            
           
 
 
@@ -231,6 +244,17 @@
     serialized_dashboard = json_response['serialized_dashboard']
 else:
     exists = True
+    # Re-fetch the dashboard_id so we can still grant permissions
+    list_resp = requests.get(
+        'https://%s/api/2.0/lakeview/dashboards' % (DOMAIN),
+        headers={'Authorization': 'Bearer %s' % token},
+        timeout=60
+    )
+    if list_resp.status_code == 200:
+        for d in list_resp.json().get('dashboards', []):
+            if d['display_name'] == 'Security Analysis Tool [SAT]':
+                dashboard_id = d['dashboard_id']
+                break
     print("Lakeview Dashboard already exists")  
 
 # COMMAND ----------
@@ -260,4 +284,36 @@
 
 # COMMAND ----------
 
+# MAGIC %md
+# MAGIC # Grant permissions so workspace users can view the dashboard
+
+# COMMAND ----------
+
+# Grant CAN_READ to the "users" group (all workspace users) so the dashboard
+# is visible to everyone, not just the service principal that created it.
+if dashboard_id:
+    perm_url = f"https://{DOMAIN}/api/2.0/permissions/dashboards/{dashboard_id}"
+    perm_body = {
+        "access_control_list": [
+            {
+                "group_name": "users",
+                "permission_level": "CAN_READ"
+            }
+        ]
+    }
+    perm_response = requests.put(
+        perm_url,
+        headers={'Authorization': 'Bearer %s' % token},
+        json=perm_body,
+        timeout=60
+    )
... (     110 total lines, truncated)
```

### `./notebooks/Setup/6. configure_alerts_template.py`

```diff
--- /var/folders/k7/vpv8ffjj5cbf6xhyk6v9xshh0000gn/T/tmp.SwRqtTEdRs/security-analysis-tool/./notebooks/Setup/6. configure_alerts_template.py	2026-02-18 23:40:42
+++ /Users/fredrik/src/origo/padda-golden-path/bundles/sat-tool/./notebooks/Setup/6. configure_alerts_template.py	2026-02-18 21:56:49
@@ -71,8 +71,12 @@
     json_.update({'token':token})
 
 db_client = SatDBClient(json_)
-token = db_client.get_temporary_oauth_token()
+oauth_token = db_client.get_temporary_oauth_token()
 
+# Prefer the notebook's native token (job runner identity) over the OAuth token
+native_token = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().getOrElse(None)
+token = native_token if native_token else oauth_token
+print(f"Using {'native notebook' if native_token else 'OAuth'} token for API calls")
 
 # COMMAND ----------
 
@@ -96,23 +100,47 @@
 
 def create_ws_folder(ws, dir_name):
     #delete tthe WS folder if it exists
-    delete_ws_folder(ws, dir_name)
+    # Try bundle path first (works for SPs that can't create under /Users/),
+    # fall back to legacy /Users/<user>/ path.
     url = "https://"+ ws.deployment_url
     headers = {"Authorization": "Bearer " + token, 'Content-type': 'application/json'}
-    path = "/Users/"+get_context().user+"/"+ dir_name
-    body = {"path":  path}
-    target_url = url + "/api/2.0/workspace/mkdirs"
-    
-    loggr.info(f"Creating {path} using {target_url}")
-    session.post(target_url, headers=headers, json=body,timeout=60).json()
-    
-    target_url = url + "/api/2.0/workspace/get-status"
-    loggr.info(f"Get Status {path} using {target_url}")
-    response=requests.get(target_url, headers=headers, json=body).json()    
-    print(response)
-    return response['object_id']
+
+    # Primary: use bundle path (SP always has access here)
+    bundle_path = f"{basePath()}/{dir_name}"
+    # Fallback: legacy /Users/<user>/ path
+    legacy_path = "/Users/"+get_context().user+"/"+ dir_name
+
+    for path in [bundle_path, legacy_path]:
+        # Delete existing folder first
+        delete_body = {"path": path, "recursive": True}
+        target_url = url + "/api/2.0/workspace/delete"
+        loggr.info(f"Deleting {path} using {target_url}")
+        try:
+            session.post(target_url, headers=headers, json=delete_body, timeout=60)
+        except Exception as e:
+            loggr.debug(f"Delete of {path} failed (may not exist): {e}")
 
+        # Create the folder
+        body = {"path": path}
+        target_url = url + "/api/2.0/workspace/mkdirs"
+        loggr.info(f"Creating {path} using {target_url}")
+        session.post(target_url, headers=headers, json=body, timeout=60)
 
+        # Verify it was created
+        target_url = url + "/api/2.0/workspace/get-status"
+        loggr.info(f"Get Status {path} using {target_url}")
+        response = requests.get(target_url, headers=headers, json=body).json()
+        print(response)
+        if 'object_id' in response:
+            loggr.info(f"Successfully created folder at {path}")
+            return response['object_id'], path
+        else:
+            loggr.warning(f"Failed to create folder at {path}: {response}")
+
+    loggr.error(f"Could not create {dir_name} folder at any location")
+    return None, None
+
+
 #delete folder that houses all SAT sql artifacts
 def get_ws_folder_object_id(ws, dir_name):
     
@@ -172,7 +200,7 @@
 
 # COMMAND ----------
 
-folder_id = create_ws_folder(ws, 'SAT_alerts')
+folder_id, folder_path = create_ws_folder(ws, 'SAT_alerts')
 
 # COMMAND ----------
 
@@ -251,7 +279,7 @@
                         "Security Analysis Tool"
                         ],
                         "display_name": "sat_alert_"+ws_to_load.workspace_id,
-                        "parent_path": "/Users/"+get_context().user+"/SAT_alerts",
+                        "parent_path": folder_path,
                         "parameters": [],
                         "warehouse_id": json_['sql_warehouse_id'],
                         "run_as_mode": "OWNER",
```

### `./notebooks/Setup/9. self_assess_workspace_configuration.py`

```diff
--- /var/folders/k7/vpv8ffjj5cbf6xhyk6v9xshh0000gn/T/tmp.SwRqtTEdRs/security-analysis-tool/./notebooks/Setup/9. self_assess_workspace_configuration.py	2026-02-18 23:40:42
+++ /Users/fredrik/src/origo/padda-golden-path/bundles/sat-tool/./notebooks/Setup/9. self_assess_workspace_configuration.py	2026-02-18 18:28:13
@@ -12,10 +12,6 @@
 
 # COMMAND ----------
 
-# MAGIC %pip install PyYAML
-
-# COMMAND ----------
-
 # MAGIC %run ../Includes/install_sat_sdk
 
 # COMMAND ----------
```

### `./notebooks/Utils/initialize.py`

```diff
--- /var/folders/k7/vpv8ffjj5cbf6xhyk6v9xshh0000gn/T/tmp.SwRqtTEdRs/security-analysis-tool/./notebooks/Utils/initialize.py	2026-02-18 23:40:42
+++ /Users/fredrik/src/origo/padda-golden-path/bundles/sat-tool/./notebooks/Utils/initialize.py	2026-02-18 15:35:59
@@ -45,12 +45,17 @@
 
 import json
 
+def _quote_schema(schema_str):
+    """Backtick-quote each part of a catalog.schema identifier so hyphens are valid SQL."""
+    parts = schema_str.split(".")
+    return ".".join(f"`{p}`" for p in parts)
+
+_raw_analysis_schema = dbutils.secrets.get(scope=SECRETS_SCOPE, key="analysis_schema_name")
+
 json_ = {
     "account_id": dbutils.secrets.get(scope=SECRETS_SCOPE, key="account-console-id"),
     "sql_warehouse_id": dbutils.secrets.get(scope=SECRETS_SCOPE, key="sql-warehouse-id"),
-    "analysis_schema_name": dbutils.secrets.get(
-        scope=SECRETS_SCOPE, key="analysis_schema_name"
-    ),
+    "analysis_schema_name": _quote_schema(_raw_analysis_schema),
     "verbosity": "info",
     "maxpages":10,
     "timebetweencalls":1,
@@ -66,9 +71,9 @@
 # COMMAND ----------
 
 intermediate_schema_name = (
-    f"{json_['analysis_schema_name'].split('.')[0]}.intermediate_schema"
-    if '.' in json_['analysis_schema_name']
-    else "hive_metastore.intermediate_schema"
+    f"`{_raw_analysis_schema.split('.')[0]}`.`intermediate_schema`"
+    if '.' in _raw_analysis_schema
+    else "`hive_metastore`.`intermediate_schema`"
 )
 json_.update(
     {
```

### `./notebooks/Utils/sat_checks_config.py`

```diff
--- /var/folders/k7/vpv8ffjj5cbf6xhyk6v9xshh0000gn/T/tmp.SwRqtTEdRs/security-analysis-tool/./notebooks/Utils/sat_checks_config.py	2026-02-18 23:40:42
+++ /Users/fredrik/src/origo/padda-golden-path/bundles/sat-tool/./notebooks/Utils/sat_checks_config.py	2026-02-18 15:36:19
@@ -230,7 +230,7 @@
         print(s_sql)
         spark.sql(s_sql)
     else:
-        s_sql = 'UPDATE  "{analysis_schema_name}".account_workspaces SET '
+        s_sql = 'UPDATE  {analysis_schema_name}.account_workspaces SET '
         first_param = False
         for param in params:
             if param in apply_setting_to_all_ws_enabled:
```

### `./notebooks/brickhound/00_config.py`

```diff
--- /var/folders/k7/vpv8ffjj5cbf6xhyk6v9xshh0000gn/T/tmp.SwRqtTEdRs/security-analysis-tool/./notebooks/brickhound/00_config.py	2026-02-18 23:40:42
+++ /Users/fredrik/src/origo/padda-golden-path/bundles/sat-tool/./notebooks/brickhound/00_config.py	2026-02-18 15:35:19
@@ -80,13 +80,14 @@
 
 # Read catalog and schema from SAT configuration
 analysis_schema = dbutils.secrets.get(scope=SECRETS_SCOPE, key="analysis_schema_name")
-CATALOG = analysis_schema.split('.')[0]
-SCHEMA = analysis_schema.split('.')[1]
+# Backtick-quote identifiers so hyphens in names (e.g. dig-felles-dev-green) are valid SQL
+CATALOG = f"`{analysis_schema.split('.')[0]}`"
+SCHEMA = f"`{analysis_schema.split('.')[1]}`"
 
 # Table names (namespaced with brickhound_ prefix to avoid conflicts with SAT tables)
-VERTICES_TABLE = f"{CATALOG}.{SCHEMA}.brickhound_vertices"
-EDGES_TABLE = f"{CATALOG}.{SCHEMA}.brickhound_edges"
-COLLECTION_METADATA_TABLE = f"{CATALOG}.{SCHEMA}.brickhound_collection_metadata"
+VERTICES_TABLE = f"{CATALOG}.{SCHEMA}.`brickhound_vertices`"
+EDGES_TABLE = f"{CATALOG}.{SCHEMA}.`brickhound_edges`"
+COLLECTION_METADATA_TABLE = f"{CATALOG}.{SCHEMA}.`brickhound_collection_metadata`"
 
 print("=" * 60)
 print("BrickHound Configuration (SAT Integration)")
```

### `./notebooks/diagnosis/pre_run_config_check.py`

```diff
--- /var/folders/k7/vpv8ffjj5cbf6xhyk6v9xshh0000gn/T/tmp.SwRqtTEdRs/security-analysis-tool/./notebooks/diagnosis/pre_run_config_check.py	2026-02-18 23:40:42
+++ /Users/fredrik/src/origo/padda-golden-path/bundles/sat-tool/./notebooks/diagnosis/pre_run_config_check.py	2026-02-18 21:23:37
@@ -111,14 +111,35 @@
 
 import os
 import subprocess
-import requests
+import shutil
+import stat
 
 print("=" * 80)
 print("TRUFFLEHOG INSTALLATION CHECK")
 print("=" * 80)
 
-# Check if TruffleHog binary exists
+# Copy TruffleHog from the bundle if not already in /tmp
 trufflehog_path = "/tmp/trufflehog"
+if not os.path.exists(trufflehog_path):
+    try:
+        notebook_path = (
+            dbutils.notebook.entry_point.getDbutils()
+            .notebook().getContext().notebookPath().get()
+        )
+        bundle_root = notebook_path.rsplit("/notebooks/", 1)[0]
+        if not bundle_root.startswith("/Workspace"):
+            bundle_root = f"/Workspace{bundle_root}"
+        src = f"{bundle_root}/bin/trufflehog"
+        if os.path.exists(src):
+            shutil.copy2(src, trufflehog_path)
+            os.chmod(trufflehog_path, os.stat(trufflehog_path).st_mode | stat.S_IEXEC)
+            print(f"✅ TruffleHog copied from bundle: {src} -> {trufflehog_path}")
+        else:
+            print(f"❌ TruffleHog binary NOT found in bundle at: {src}")
+            print("   Make sure bin/trufflehog is included in your DAB sync.")
+    except Exception as e:
+        print(f"❌ Failed to copy TruffleHog from bundle: {e}")
+
 if os.path.exists(trufflehog_path):
     print(f"✅ TruffleHog binary found at: {trufflehog_path}")
 
@@ -141,15 +162,7 @@
         print(f"⚠️  Error checking TruffleHog version: {str(e)}")
 else:
     print(f"❌ TruffleHog binary NOT found at: {trufflehog_path}")
-    print()
-    print("TruffleHog Installation Instructions:")
-    print("1. TruffleHog is automatically installed when running secret scanner")
-    print("2. Manual installation:")
-    print("   %sh curl -sSfL https://raw.githubusercontent.com/trufflesecurity/trufflehog/main/scripts/install.sh | sh -s -- -b /tmp")
-    print()
-    print("Network Requirements:")
-    print("- Access to raw.githubusercontent.com (install script)")
-    print("- Access to github.com/trufflesecurity (binary download)")
+    print("   Ensure bin/trufflehog is included in the DAB bundle sync.")
 
 print()
 
@@ -163,26 +176,6 @@
 print("=" * 80)
 print("NETWORK ACCESS CHECK (TRUFFLEHOG)")
 print("=" * 80)
-
-# Test access to GitHub raw content
-github_urls = [
-    "https://raw.githubusercontent.com/trufflesecurity/trufflehog/main/scripts/install.sh",
-    "https://github.com/trufflesecurity/trufflehog/releases"
-]
-
-for url in github_urls:
-    try:
-        response = requests.head(url, timeout=10)
-        if response.status_code == 200:
-            print(f"✅ Access OK: {url}")
-        else:
-            print(f"⚠️  Access issue ({response.status_code}): {url}")
-    except requests.exceptions.Timeout:
-        print(f"❌ Timeout accessing: {url}")
-    except requests.exceptions.ConnectionError:
-        print(f"❌ Connection failed: {url}")
-        print("   ACTION: Allowlist GitHub domains in firewall")
-    except Exception as e:
-        print(f"❌ Error accessing {url}: {str(e)}")
-
+print("ℹ️  TruffleHog is bundled in the DAB — no network access to GitHub required.")
+print("   Binary is copied from the bundle at runtime.")
 print()
```

### `./notebooks/security_analysis_driver.py`

```diff
--- /var/folders/k7/vpv8ffjj5cbf6xhyk6v9xshh0000gn/T/tmp.SwRqtTEdRs/security-analysis-tool/./notebooks/security_analysis_driver.py	2026-02-18 23:40:42
+++ /Users/fredrik/src/origo/padda-golden-path/bundles/sat-tool/./notebooks/security_analysis_driver.py	2026-02-18 16:20:21
@@ -47,12 +47,18 @@
 
 import json
 
-out = dbutils.notebook.run(
-    f"{basePath()}/notebooks/Utils/accounts_bootstrap",
-    3000,
-    {"json_": json.dumps(json_), "origin": "driver"},
-)
-loggr.info(out)
+# accounts_bootstrap requires the Accounts API which is unreachable in
+# SRA/isolated-network environments. Skip gracefully and continue with
+# workspace-level analysis only.
+try:
+    out = dbutils.notebook.run(
+        f"{basePath()}/notebooks/Utils/accounts_bootstrap",
+        3000,
+        {"json_": json.dumps(json_), "origin": "driver"},
+    )
+    loggr.info(out)
+except Exception as e:
+    loggr.warning(f"Account bootstrap skipped (expected in SRA/isolated mode): {e}")
 
 # COMMAND ----------
 
```

### `./notebooks/security_analysis_initializer.py`

```diff
--- /var/folders/k7/vpv8ffjj5cbf6xhyk6v9xshh0000gn/T/tmp.SwRqtTEdRs/security-analysis-tool/./notebooks/security_analysis_initializer.py	2026-02-18 23:40:42
+++ /Users/fredrik/src/origo/padda-golden-path/bundles/sat-tool/./notebooks/security_analysis_initializer.py	2026-02-18 18:06:48
@@ -32,25 +32,37 @@
 
 # COMMAND ----------
 
-def run_notebook(notebook_path, timeout):
-    status = dbutils.notebook.run(notebook_path, timeout)
-    if status != "OK":
-        loggr.exception(f"Error Encountered in {notebook_path}", status)
-        dbutils.notebook.exit()
+def run_notebook(notebook_path, timeout, required=True):
+    try:
+        status = dbutils.notebook.run(notebook_path, timeout)
+        if status != "OK":
+            msg = f"Error in {notebook_path}: {status}"
+            if required:
+                raise Exception(msg)
+            loggr.warning(msg)
+    except Exception as e:
+        if required:
+            raise
+        loggr.warning(f"Optional step failed: {notebook_path} — {e}")
 
 # COMMAND ----------
 
+# Steps 1 (list_account_workspaces) and 3 (test_connections) require the
+# Accounts API which is unreachable in SRA/isolated-network environments.
+# A pre-populated workspace_configs.csv is bundled in configs/ instead.
+#
+# Steps 4 and 9 are required (load config into tables).
+# Steps 5 (dashboard) and 6 (alerts) are optional — they need a SQL warehouse
+# and will be retried on next run if they fail.
 notebooks = [
-    ("1. list_account_workspaces_to_conf_file", 3000),
-    ("3. test_connections", 12000),
-    ("4. enable_workspaces_for_sat", 3000),
-    ("5. import_dashboard_template_lakeview", 3000),
-    ("6. configure_alerts_template", 3000),
-    ("9. self_assess_workspace_configuration", 3000),
+    ("4. enable_workspaces_for_sat", 3000, True),
+    ("5. import_dashboard_template_lakeview", 3000, False),
+    ("6. configure_alerts_template", 3000, False),
+    ("9. self_assess_workspace_configuration", 3000, True),
 ]

-for notebook, timeout in notebooks:
-    status=run_notebook(f"{basePath()}/notebooks/Setup/{notebook}", timeout)
+for notebook, timeout, required in notebooks:
+    run_notebook(f"{basePath()}/notebooks/Setup/{notebook}", timeout, required)

 # COMMAND ----------

```


---

## How to Update from Upstream

To incorporate future upstream changes:

1. Clone the upstream repo:
   ```bash
   git clone https://github.com/databricks-industry-solutions/security-analysis-tool.git /tmp/sat-upstream
   ```

2. Compare with local:
   ```bash
   diff -rq /tmp/sat-upstream/src/dabs/notebooks/ bundles/sat-tool/notebooks/
   ```

3. Review and selectively merge changes:
   ```bash
   # For each changed file, review the diff:
   diff -u /tmp/sat-upstream/src/dabs/notebooks/FILE bundles/sat-tool/notebooks/FILE
   ```

4. Re-run this script to update this diff document.
