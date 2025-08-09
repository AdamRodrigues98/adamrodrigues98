# AWS CLI - Comandos e Configurações

Este guia contém exemplos práticos para configuração e uso do AWS CLI envolvendo **RDS**, **DMS** e **Replication Tasks**.

---

## 📑 Índice

1. [Configuração inicial](#configuração-inicial)
2. [Arquivo `~/.aws/config`](#arquivo-awsconfig)
3. [Arquivo `~/.aws/credentials`](#arquivo-awscredentials)
4. [Comandos RDS](#comandos-rds)
5. [Restaurar Snapshot e Ajustar Parâmetros](#restaurar-snapshot-e-ajustar-parâmetros)
6. [Criar novas instâncias RDS](#criar-novas-instâncias-rds)
7. [Configuração DMS](#configuração-dms)
8. [DMS Serverless](#dms-serverless)
9. [Instância DMS](#instância-dms)
10. [Subnet DMS](#subnet-dms)
11. [Replication Tasks](#replication-tasks)
12. [Gerenciar Tasks](#gerenciar-tasks)

---

## Configuração inicial

```bash
mkdir -p ~/.aws
nano ~/.aws/credentials
nano ~/.aws/config
```

## Arquivo ~/.aws/config
```bash
[profile qa]
role_arn = arn:aws:iam::(id-conta):role/dba
source_profile = db-name-identity
region = us-east-1
output = json
```

## Arquivo ~/.aws/credentials
```bash
[default]
region = us-east-1
output = json

[nexti]
aws_access_key_id = XXXXXXXXXXXXXXXXXXXX
aws_secret_access_key = XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

## Comandos RDS
```bash
aws rds modify-db-instance \
    --db-instance-identifier db-name-dev-2025-01-02-06-06 \
    --backup-retention-period 1 \
    --db-parameter-group-name dbdev \
    --apply-immediately \
    --profile dev

aws rds create-db-instance-read-replica \
    --db-instance-identifier db-name-dev-read \
    --source-db-instance-identifier db-name-dev-2025-01-02-06-06 \
    --availability-zone us-east-1c \
    --storage-type gp3 \
    --db-instance-class db.m6i.large \
    --profile dev

aws rds modify-db-instance \
    --db-instance-identifier db-name-dev-read \
    --db-parameter-group-name time-tracking-read-dev \
    --apply-immediately \
    --profile dev

aws rds reboot-db-instance \
    --db-instance-identifier db-name-dev-read \
    --profile dev

aws rds describe-db-snapshots --profile qa
```

## Restaurar Snapshot e Ajustar Parâmetros
```bash
aws rds restore-db-instance-from-db-snapshot \
    --profile qa \
    --db-instance-identifier db-name-mov \
    --db-snapshot-identifier arn:aws:rds:us-east-1:(id-conta):snapshot:db-name-master-8-2025-04-10-03-00 \
    --db-instance-class db.m7g.large \
    --storage-type gp3 \
    --iops 12000 \
    --engine mysql \
    --availability-zone us-east-1b \
    --db-subnet-group-name rds-subnet-group-varejo \
    --vpc-security-group-ids sg-0104e41f2c9fc9083

aws rds modify-db-instance \
    --db-instance-identifier db-name-scalability \
    --db-parameter-group-name qa-scalability-80 \
    --apply-immediately \
    --profile qa

aws rds reboot-db-instance \
    --db-instance-identifier db-name-scalability \
    --profile qa
```

## Criar novas instâncias RDS
```bash
aws rds create-db-instance \
    --db-instance-identifier time-master \
    --allocated-storage 1000 \
    --db-instance-class db.m7g.large \
    --engine mysql \
    --engine-version 8.4.5 \
    --master-username db-name \
    --master-user-password FzX8t0d#ta \
    --storage-type gp3 \
    --availability-zone us-east-1b \
    --backup-retention-period 0 \
    --no-multi-az \
    --db-parameter-group-name time-tracking-qa-scalability-80 \
    --db-subnet-group-name rds-subnet-group \
    --vpc-security-group-ids sg-nome-sg \
    --profile qa

aws rds create-db-instance \
    --db-instance-identifier clocking-master \
    --allocated-storage 1000 \
    --db-instance-class db.m6i.large \
    --engine mysql \
    --engine-version 8.4.5 \
    --master-username (usuario) \
    --master-user-password (senha) \
    --storage-type gp3 \
    --availability-zone us-east-1b \
    --backup-retention-period 0 \
    --no-multi-az \
    --db-parameter-group-name qa-scalability-80 \
    --db-subnet-group-name rds-subnet-group \
    --vpc-security-group-ids sg-nome-sg \
    --profile qa

aws rds create-db-instance \
    --db-instance-identifier varejo-master \
    --allocated-storage 100 \
    --db-instance-class db.t3.medium \
    --engine mysql \
    --engine-version 8.4.5 \
    --master-username (usuario) \
    --master-user-password (senha) \
    --storage-type gp3 \
    --availability-zone us-east-1b \
    --backup-retention-period 0 \
    --no-multi-az \
    --db-parameter-group-name qa-scalability-80 \
    --db-subnet-group-name rds-subnet-group \
    --vpc-security-group-ids sg-nome-sg \
    --profile qa
```

## Configuração DMS
```bash
aws dms create-endpoint \
    --endpoint-identifier scalability-mysql \
    --endpoint-type source \
    --engine-name mysql \
    --username (usuario) \
    --password (senha) \
    --server-name db-name-scalability.cavowrefpq34.us-east-1.rds.amazonaws.com \
    --port 3306 \
    --database-name db-name \
    --profile qa

aws dms create-endpoint \
    --endpoint-identifier time-master \
    --endpoint-type target \
    --engine-name mysql \
    --username db-name \
    --password FzX8t0d#ta \
    --server-name time-master.cavowrefpq34.us-east-1.rds.amazonaws.com \
    --port 3306 \
    --database-name db-name \
    --profile qa

aws dms describe-endpoints --profile qa
```

## DMS Serverless
```bash
aws dms create-replication-config \
    --replication-config-identifier batch-eticket \
    --source-endpoint-arn arn:aws:dms:us-east-1:(id-conta):endpoint:HX5VR3UBX5GYXHP5XM3CG6RQ6Y \
    --target-endpoint-arn arn:aws:dms:us-east-1:(id-conta):endpoint:3SQH3WDZPFEQZEJARQQH6UGZZE \
    --replication-type full-load \
    --compute-config '{ "MaxCapacityUnits": 8, "MinCapacityUnits": 4 }' \
    --table-mappings "file:///home/adam.rodrigues/Documentos/rock_seg/dms/tables/table-mappings_old.json" \
    --profile qa
```

## Instância DMS
```bash
aws dms create-replication-instance \
    --replication-instance-identifier scalability-dms-instance \
    --replication-instance-class dms.t3.medium \
    --allocated-storage 200 \
    --replication-subnet-group-identifier dms-subnet-group \
    --vpc-security-group-ids sg-nome-sg \
    --no-multi-az \
    --profile qa
```

## Subnet DMS
```bash
aws dms create-replication-subnet-group \
    --replication-subnet-group-identifier dms-subnet-group \
    --replication-subnet-group-description "Subnet Group for DMS Replication" \
    --subnet-ids subnet-0b096193751e2e0e7 subnet-0e3ce0f1a187174db subnet-01afa3788bbbc2768 subnet-0ed8051675d793656 subnet-039e56da1525e0dca subnet-0a21b46e47852100a \
    --profile qa
```

## Replication Tasks

```bash
aws dms create-replication-task \
    --replication-task-identifier replication-time-tracking \
    --migration-type full-load-and-cdc \
    --replication-instance-arn arn:aws:dms:us-east-1:(id-conta):rep:XDBXYWCCCBDLTCXOBKMOG42UQM \
    --source-endpoint-arn arn:aws:dms:us-east-1:(id-conta):endpoint:HX5VR3UBX5GYXHP5XM3CG6RQ6Y \
    --target-endpoint-arn arn:aws:dms:us-east-1:(id-conta):endpoint:RDSBYL4WFRB5ZCWTZ4VHPY26AE \
    --table-mappings file:///home/adam.rodrigues/Documentos/rock_seg/dms/tables/time_tracking/mappings/replicacao/table-mappings.json \
    --replication-task-settings file:///home/adam.rodrigues/Documentos/rock_seg/dms/tables/time_tracking/mappings/replicacao/task-settings.json \
    --profile qa
```

## Gerenciar Tasks

```bash
aws dms describe-replication-tasks --profile qa

aws dms stop-replication-task \
    --replication-task-arn arn:aws:dms:us-east-1:(id-conta):task:GW2CDORULRBS5L2MYKON7SZ2J4 \
    --profile qa

aws dms modify-replication-task \
    --replication-task-arn arn:aws:dms:us-east-1:(id-conta):task:GW2CDORULRBS5L2MYKON7SZ2J4 \
    --replication-task-settings '{"LoadFileSize": 50}' \
    --profile qa

aws dms start-replication-task \
    --replication-task-arn arn:aws:dms:us-east-1:(id-conta):task:GW2CDORULRBS5L2MYKON7SZ2J4 \
    --start-replication-task-type resume-processing \
    --profile qa

aws dms describe-replication-tasks \
    --filters "Name=replication-task-arn,Values=arn:aws:dms:us-east-1:(id-conta):task:L3627XWQPVE6HH2D263ALFM2SI" \
    --query "ReplicationTasks[*].{Status:Status,ReplicationTaskStats:ReplicationTaskStats}" \
    --profile qa

```