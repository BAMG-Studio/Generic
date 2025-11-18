terraform {
  required_version = ">= 1.6.0"
}

# basic sanity output so terraform plan/apply are no-ops
output "test_message" {
  value       = "ExecutiveDisorderLive test stub"
  description = "Dummy output emitted to prove the Terraform module wires correctly."
}
