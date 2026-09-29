const assert = require('assert');

// Test data replicating live backend alerts and edge cases
const mockAnomalies = [
  {
    alert_id: 'ALT-31F5688A',
    consumer_id: 'CONS_COM_004',
    consumer_name: 'Saravana Bhavan Sweets',
    area: 'Kodambakkam',
    risk_score: 0.79,
    risk_tier: 'HIGH',
    estimated_unbilled_kwh: 0.0,
    anomaly_score: 0.4871
  },
  {
    alert_id: 'ALT-503ED3DB',
    consumer_id: 'CONS_COM_015',
    consumer_name: 'Guindy Precision Tools',
    area: 'Guindy',
    risk_score: 0.77,
    risk_tier: 'HIGH',
    estimated_unbilled_kwh: 879.852,
    anomaly_score: 0.3695
  },
  {
    alert_id: 'ALT-GENUINE-ZERO',
    consumer_id: 'CONS_NORMAL_001',
    consumer_name: 'Verified Balanced Unit',
    area: 'Adyar',
    risk_score: 0.72,
    risk_tier: 'MEDIUM',
    estimated_unbilled_kwh: 0,
    calculated_zero: true,
    loss_calculated: true
  },
  {
    alert_id: 'ALT-MISSING-NULL',
    consumer_id: 'CONS_NULL_002',
    consumer_name: 'Unestimated Anomaly Account',
    area: 'Anna Nagar',
    risk_score: 0.82,
    risk_tier: 'HIGH',
    estimated_unbilled_kwh: null,
    anomaly_score: 0.55
  },
  {
    alert_id: 'ALT-MISSING-UNDEF',
    consumer_id: 'CONS_UNDEF_003',
    consumer_name: 'Missing Loss Field Account',
    area: 'T. Nagar',
    risk_score: 0.85,
    risk_tier: 'CRITICAL',
    // estimated_unbilled_kwh undefined
  }
];

function formatINR(amount) {
  if (amount === null || amount === undefined || isNaN(amount)) return '\u20b90';
  return '\u20b9' + Math.round(amount).toLocaleString('en-IN');
}

function renderRow(item) {
  const riskVal = item.risk_score > 1 ? Math.round(item.risk_score) : Math.round(item.risk_score * 100);

  const isGenuineZero = Boolean(
    item.is_genuine_zero === true ||
    item.calculated_zero === true ||
    item.is_calculated_zero === true ||
    item.loss_status === 'CALCULATED_ZERO' ||
    item.has_genuine_zero === true ||
    (item.loss_calculated === true && (item.estimated_unbilled_kwh === 0 || item.estimated_unbilled_kwh === 0.0))
  );

  const hasValidLoss = item.estimated_unbilled_kwh !== null &&
    item.estimated_unbilled_kwh !== undefined &&
    item.estimated_unbilled_kwh !== '' &&
    !isNaN(Number(item.estimated_unbilled_kwh)) &&
    Number(item.estimated_unbilled_kwh) > 0;

  let unitsPrimary = '';
  let unitsSecondary = '';
  let lossPrimary = '';
  let lossSecondary = '';

  if (hasValidLoss) {
    unitsPrimary = `${Math.round(item.estimated_unbilled_kwh).toLocaleString('en-IN')} Units`;
    lossPrimary = formatINR((item.estimated_unbilled_kwh || 0) * 8);
  } else if (isGenuineZero) {
    unitsPrimary = '0 Units';
    lossPrimary = '₹0';
  } else {
    unitsPrimary = 'Not estimated';
    unitsSecondary = 'Flagged by behavioural anomaly';
    lossPrimary = 'Not estimated';
    lossSecondary = 'Loss estimate unavailable';
  }

  return {
    consumer: item.consumer_name,
    riskScoreDisplay: `${riskVal}/100`,
    unitsPrimary,
    unitsSecondary,
    lossPrimary,
    lossSecondary
  };
}

// 1. Test Saravana Bhavan Sweets (anomaly-only case with 0.0 unbilled)
const case1 = renderRow(mockAnomalies[0]);
console.log('Case 1 (Saravana Bhavan Sweets):', case1);
assert.strictEqual(case1.riskScoreDisplay, '79/100');
assert.strictEqual(case1.unitsPrimary, 'Not estimated');
assert.strictEqual(case1.unitsSecondary, 'Flagged by behavioural anomaly');
assert.strictEqual(case1.lossPrimary, 'Not estimated');
assert.strictEqual(case1.lossSecondary, 'Loss estimate unavailable');

// 2. Test Guindy Precision Tools (valid calculated case)
const case2 = renderRow(mockAnomalies[1]);
console.log('Case 2 (Guindy Precision Tools):', case2);
assert.strictEqual(case2.riskScoreDisplay, '77/100');
assert.strictEqual(case2.unitsPrimary, '880 Units');
assert.strictEqual(case2.unitsSecondary, '');
assert.strictEqual(case2.lossPrimary, '₹7,039');
assert.strictEqual(case2.lossSecondary, '');

// 3. Test Genuine Calculated Zero case
const case3 = renderRow(mockAnomalies[2]);
console.log('Case 3 (Genuine Calculated Zero):', case3);
assert.strictEqual(case3.unitsPrimary, '0 Units');
assert.strictEqual(case3.lossPrimary, '₹0');

// 4. Test Missing (null) case
const case4 = renderRow(mockAnomalies[3]);
console.log('Case 4 (Missing null):', case4);
assert.strictEqual(case4.unitsPrimary, 'Not estimated');
assert.strictEqual(case4.lossPrimary, 'Not estimated');

// 5. Test Missing (undefined) case
const case5 = renderRow(mockAnomalies[4]);
console.log('Case 5 (Missing undefined):', case5);
assert.strictEqual(case5.unitsPrimary, 'Not estimated');
assert.strictEqual(case5.lossPrimary, 'Not estimated');

console.log('\nAll 5 assertions passed successfully!');
