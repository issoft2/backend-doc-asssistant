

mysql -u root -p -D euracare -e "
 SELECT pv.patient_id AS 'Patient_Id', p.fname AS 'First_Name', p.mname AS 'Middle_Name', p.lname AS 'Last_Name', v.name AS 'vital_name', pv.value AS 'vital_value', v.unit AS 'unit', pv.read_date AS 'read_at', st.firstname AS 'read_by_first_name', st.lastname AS 'read_by_last_name' 
 FROM vital_sign pv 
 LEFT JOIN vital v ON pv.type_id=v.id 
 LEFT JOIN staff_directory st ON pv.read_by = st.staffId 
 LEFT JOIN patient_demograph p ON pv.patient_id=p.patient_ID
 INTO OUTFILE '/var/lib/mysql-files/patient_vital_report.csv'
 FIELDS TERMINATED BY ',' 
 ENCLOSED BY '\"' 
 LINES TERMINATED BY '\n';
"


mysql -u root -p -D euracare -e "
SELECT ins.scheme_name AS 'INSURANCE SCHEME', 
       ins.pay_type AS 'INSURANCE_TYPE', 
       inso.company_name AS 'Insurance Scheme Owner', 
       ins.credit_limit AS 'Scheme Credit Limit', 
       ins.reg_cost_individual AS 'Individual Reg Cost', 
       ins.reg_cost_company AS 'Company Reg. Cost', 
       ins.email AS 'Email Address', 
       ins.phone AS 'Phone Number', 
       ins.active AS 'Status' 
FROM insurance_schemes ins 
LEFT JOIN insurance_owners inso ON ins.scheme_owner_id = inso.id 
INTO OUTFILE '/var/lib/mysql-files/euracare_insurance_scheme_report.csv'
FIELDS TERMINATED BY ',' 
ENCLOSED BY '\"' 
LINES TERMINATED BY '\n';
"

mysql -u root -p -D euracare -e "
SELECT bl.item_code as 'Service Code', bl.item_description as 'Service Name' 
FROM  insurance_billable_items bl wHERE bl.active IS TRUE
INTO OUTFILE '/var/lib/mysql-files/euracare_billable_items.csv'
FIELDS TERMINATED BY ',' 
ENCLOSED BY '\"' 
LINES TERMINATED BY '\n';
"

mysql -u root -p -D euracare -e "
SELECT ico.item_code AS 'Service Code', ins.scheme_name as 'Scheme Name', ico.selling_price AS 'Selling Price', ico.followUpPrice AS 'Follow Up Price', ico.theatrePrice AS 'Theatre Price', ico.anaesthesiaPrice as 'Anaesthesia Price', ico.surgeonPrice as 'Surgeon Price', ico.type AS 'Price Type', ico.capitated as 'Capitated?'
FROM insurance_items_cost ico LEFT JOIN insurance_schemes ins ON ico.insurance_scheme_id=ins.id
INTO OUTFILE '/var/lib/mysql-files/euracare_insurance_item_cost.csv'
FIELDS TERMINATED BY ',' 
ENCLOSED BY '\"' 
LINES TERMINATED BY '\n';
"

mysql -u root -p euracare -e "
SELECT
    'service_category',
    'service_name',
    'item_code',
    'selling_price',
    'followUpPrice',
    'theatrePrice',
    'anaesthesiaPrice',
    'surgeonPrice',
    'co_pay',
    'service_type',
    'Capitated'
UNION ALL
SELECT 
    bs.name,
    ibi.item_description,
    iic.item_code,
    iic.selling_price,
    iic.followUpPrice,
    iic.theatrePrice,
    iic.anaesthesiaPrice,
    iic.surgeonPrice,
    iic.co_pay,
    iic.type,
    iic.capitated
FROM insurance_items_cost iic
JOIN insurance_billable_items ibi 
    ON iic.item_code = ibi.item_code
JOIN bills_source bs 
    ON ibi.item_group_category_id = bs.id
WHERE 
   ibi.active = 1 and 
ORDER BY service_category, service_name;
" | sed 's/\t/,/g' > euracare_private_insurance_services.csv

// drugs

mysql -u root -p euracare -e "
SELECT
    'Drug_Name',
    'Drug_Generic',
    'Batch_Name',
    'Quantity',
    'Expiration_Date',
    'Generic Form',
    'Generic Weight'
UNION ALL
SELECT
    REPLACE(d.name, ',', ''),
    REPLACE(dg.name, ',', ''),
    REPLACE(db.name, ',', ''),
    REPLACE(db.quantity, ',', ''),
    REPLACE(db.expiration_date, ',', ''),
    REPLACE(dg.form, ',', ''),
    REPLACE(dg.weight, ',', '')
FROM
    drugs d
LEFT JOIN
    drug_generics dg ON d.drug_generic_id = dg.id
LEFT JOIN
    drug_batch db ON db.drug_id = d.id
WHERE
    db.quantity != 0 AND dg.active is true
ORDER BY
    Drug_Generic, Drug_Name;
" | sed 's/\t/,/g' > drug_list_report.csv



mysql -u root -p euracare -e "
SELECT
    'Claim_id',
    'Processed_Date',
    'Patient_Name',
    'Description',
    'Diagnosis',
    'Reason',
    'Patient_Id',
    'Scheme',
    'Service',
    'Transaction_Date',
    'Quantity',
    'Amount',
    'Status',
    'Type'
UNION ALL
SELECT
    REPLACE(cb.claim_id, ',', ' ') as Claim_id, 
    REPLACE(DATE(c.create_date), ',', ' ') as Processed_Date, 
    REPLACE(c.patient_name, ',', ' ') as Patient_Name, 
    REPLACE(cb.description, ',', ' ') as Description, 
    REPLACE(c.diagnoses, ',', ' ') as Diagnosis, 
    REPLACE(c.reason, ',', ' ') as Reason, 
    REPLACE(c.patient_id, ',', ' ') as Patient_Id, 
    REPLACE(cb.insurance, ',', ' ') as Scheme,  
    REPLACE(cb.service, ',', ' ') as Service,   
    REPLACE(DATE(cb.trans_date), ',', ' ') as Transaction_Date, 
    REPLACE(cb.quantity, ',', ' ') as Quantity, 
    REPLACE(cb.amount, ',', ' ') as Amount,
    REPLACE(c.status, ',', '') as Status,
    REPLACE(c.type, ',', '') as Type 
FROM 
claim_bill_lines cb  
LEFT JOIN claim c ON c.id = cb.claim_id 
" > claim_invoice_report.csv


mysql -u root -p euracare -e "
(SELECT 
    'test_id', 'test_name', 'test_category', 'template_name', 
    'template_data', 'lab_method'
UNION ALL
SELECT 
    ltc.id, REPLACE(ltc.name, ',', ''), REPLACE(tc.name, ',', ''),
    REPLACE(lt.label, ',', ''), REPLACE(ltd.label, ',', ''),
    REPLACE(COALESCE(lm.name, ''), ',', '')
FROM labtests_config ltc
LEFT JOIN labtests_config_category tc ON ltc.category_id = tc.id
LEFT JOIN lab_template lt ON lt.id = ltc.lab_template_id AND lt.active = 1
LEFT JOIN lab_template_data ltd ON ltd.lab_template_id = lt.id
LEFT JOIN lab_method lm ON lm.id = ltd.lab_method_id AND lm.active = 1
WHERE ltc.active = 1 GROUP BY ltc.name) ;
" > lab_tests_templates_methods_config.csv

mysql -u root -p euracare -e "
SELECT
    'ID',
    'Name',
    'Unit',
    'Min_Value',
    'Max_Value',
    'Pattern'
UNION ALL
SELECT
    id,
    REPLACE(name, ',', ''),
    REPLACE(unit, ',', ''),
    REPLACE(min_val, ',', ''),
    REPLACE(max_val, ',', ''),
    REPLACE(pattern, ',', '')
FROM vital
ORDER BY name;
" | sed 's/\t/,/g' > vital_signs.csv



#!/bin/bash
# Prompt once
read -s -p "MySQL password for root: " MYSQL_PWD_INPUT
echo

mysql -u root -p"$MYSQL_PWD_INPUT" euracare -Ns -e "SELECT id, scheme_name FROM insurance_schemes WHERE active = 1" \
| while IFS=$'\t' read -r scheme_id scheme_name; do
  if [ -z "$scheme_id" ] || [ -z "$scheme_name" ]; then
    echo "Skipping empty row: scheme_id=[$scheme_id], scheme_name=[$scheme_name]"
    continue
  fi

  echo "Processing scheme_id=[$scheme_id], scheme_name=[$scheme_name]"

  safe_name=$scheme_name
  safe_name=${safe_name// /_}
  safe_name=${safe_name//\//_}
  safe_name=${safe_name//\\/}
  safe_name=${safe_name//\"/}
  safe_name=${safe_name//\'/}
  safe_name=${safe_name//[^A-Za-z0-9_.-]/_}

  filename="euracare_${scheme_id}_${safe_name}_services.csv"
  echo "Writing to file: $filename"

  mysql -u root -p"$MYSQL_PWD_INPUT" euracare -e "
  SELECT
      'scheme_id','scheme_name',
      'service_category','service_name','item_code',
      'selling_price','followUpPrice','theatrePrice',
      'anaesthesiaPrice','surgeonPrice','co_pay',
      'service_type','Capitated'
  UNION ALL
  SELECT 
      ins.id AS scheme_id,
      -- Clean scheme_name
      REPLACE(
        REPLACE(
          REPLACE(
            REPLACE(ins.scheme_name, '\r', ''),
          '\n', ''),
        ',', ' '),
      '\"', '') AS scheme_name,
      -- Clean service_category
      REPLACE(
        REPLACE(
          REPLACE(
            REPLACE(bs.name, '\r', ''),
          '\n', ''),
        ',', ' '),
      '\"', '') AS service_category,
      -- Clean service_name
      REPLACE(
        REPLACE(
          REPLACE(
            REPLACE(ibi.item_description, '\r', ''),
          '\n', ''),
        ',', ' '),
      '\"', '') AS service_name,
      iic.item_code,
      iic.selling_price,
      iic.followUpPrice,
      iic.theatrePrice,
      iic.anaesthesiaPrice,
      iic.surgeonPrice,
      iic.co_pay,
      iic.type,
      iic.capitated
  FROM insurance_items_cost iic
  JOIN insurance_billable_items ibi 
      ON iic.item_code = ibi.item_code
  JOIN bills_source bs 
      ON ibi.item_group_category_id = bs.id
  JOIN insurance_schemes ins
      ON iic.insurance_scheme_id = ins.id
  WHERE 
    ins.id = ${scheme_id}
  " | sed 's/\t/,/g' > "$filename"

  echo "Exported $filename"
done

