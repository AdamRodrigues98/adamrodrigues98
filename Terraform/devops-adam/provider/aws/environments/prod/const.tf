locals {
  organization_name         = "adam"
  account_name              = "prod"
  account_region            = "us-east-1"
  organization_account_name = format("%s-%s", local.organization_name, local.account_name)
}
locals {
  accounts = {
    adam-prod = "99999999999"
  }
  dnsprivate = {
    dns_name = format("%s.%s.private", local.account_name, local.organization_name)
  }
  dnspublic = {
    dns_name = format("%s.%s.com", local.account_name, local.organization_name)
  }
  dnspublic_without_account_prefix = {
    dns_name = format("%s.com", local.organization_name)
  }
}