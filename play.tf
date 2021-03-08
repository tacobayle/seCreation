resource "null_resource" "local_file" {
  provisioner "local-exec" {
    command = "ansible-playbook play2.yaml --extra-vars '{\"no_access_vcenter\": ${jsonencode(var.no_access_vcenter)}}' --extra-vars '{\"vsphere_username\": ${jsonencode(var.vsphere_username)}}' --extra-vars '{\"vsphere_password\": ${jsonencode(var.vsphere_password)}}'"
  }
}
