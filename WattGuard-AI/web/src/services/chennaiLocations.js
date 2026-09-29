/**
 * WattGuard AI - Chennai Geographic & Localization Matrix
 * Maps smart meter consumers and tactical inspection squads to authentic Chennai coordinates.
 */

export const CHENNAI_CENTER = [13.0827, 80.2707];

export const CHENNAI_NEIGHBORHOOD_COORDS = {
  'T. Nagar': {
    base: [13.0418, 80.2341],
    streets: {
      'Usman Road': [13.0418, 80.2341],
      'South Boag Road': [13.0385, 80.2395],
      'GN Chetty Road': [13.0450, 80.2415],
      'Pondy Bazaar': [13.0405, 80.2325],
      'Ranganathan Street': [13.0425, 80.2310],
      'Panagal Park': [13.0410, 80.2335]
    }
  },
  'Anna Nagar': {
    base: [13.0850, 80.2100],
    streets: {
      '2nd Avenue': [13.0850, 80.2100],
      'Shanthi Colony': [13.0882, 80.2155],
      '12th Main Road': [13.0865, 80.2080],
      'Roundtana': [13.0845, 80.2120]
    }
  },
  'Nungambakkam': {
    base: [13.0600, 80.2400],
    streets: {
      'College Road': [13.0645, 80.2425],
      'Sterling Road': [13.0610, 80.2380],
      'Nungambakkam High Road': [13.0585, 80.2440]
    }
  },
  'Kodambakkam': {
    base: [13.0500, 80.2200],
    streets: {
      'Arcot Road': [13.0512, 80.2215],
      'Trustpuram': [13.0495, 80.2245],
      'Station Road': [13.0480, 80.2260]
    }
  },
  'Adyar': {
    base: [13.0064, 80.2575],
    streets: {
      'LB Road': [13.0064, 80.2575],
      'Sardar Patel Road': [13.0090, 80.2530],
      'Kasturibai Nagar': [13.0075, 80.2545],
      'Adyar Depot': [13.0055, 80.2565]
    }
  },
  'Velachery': {
    base: [12.9790, 80.2210],
    streets: {
      'Velachery Main Road': [12.9790, 80.2210],
      'Bypass': [12.9755, 80.2235],
      'Vijaya Nagar': [12.9815, 80.2195]
    }
  },
  'Guindy': {
    base: [13.0067, 80.2026],
    streets: {
      'SIDCO Industrial Estate': [13.0067, 80.2026],
      'Anna Salai': [13.0110, 80.2075],
      'Inner Ring Road': [13.0040, 80.2005],
      'Kathipara': [13.0085, 80.2052]
    }
  },
  'Mylapore': {
    base: [13.0368, 80.2676],
    streets: {
      'Luz Church Road': [13.0368, 80.2676],
      'Kutchery Road': [13.0335, 80.2710],
      'Royapettah High Road': [13.0400, 80.2640]
    }
  },
  'Saidapet': {
    base: [13.0210, 80.2230],
    streets: {
      'Anna Salai': [13.0210, 80.2230],
      'Jones Road': [13.0245, 80.2210]
    }
  },
  'Perungudi': {
    base: [12.9654, 80.2461],
    streets: {
      'OMR': [12.9654, 80.2461],
      'Kandanchavadi': [12.9680, 80.2440]
    }
  },
  'Thoraipakkam': {
    base: [12.9380, 80.2345],
    streets: {
      'OMR': [12.9380, 80.2345],
      '200 Feet Radial Road': [12.9410, 80.2320]
    }
  },
  'Pallavaram': {
    base: [12.9675, 80.1491],
    streets: {
      'GST Road': [12.9675, 80.1491],
      'Pammal Main Road': [12.9690, 80.1470]
    }
  },
  'Chromepet': {
    base: [12.9516, 80.1412],
    streets: {
      'GST Road': [12.9516, 80.1412],
      'Station Road': [12.9525, 80.1435],
      'Radha Nagar': [12.9490, 80.1390]
    }
  },
  'Tambaram': {
    base: [12.9249, 80.1000],
    streets: {
      'GST Road': [12.9249, 80.1000],
      'Shanmugam Road': [12.9260, 80.1020],
      'Mudichur Road': [12.9230, 80.0980]
    }
  }
};

/**
 * Deterministic hash of string into positive integer.
 */
function hashString(str) {
  let hash = 0;
  for (let i = 0; i < (str || '').length; i++) {
    hash = (hash << 5) - hash + str.charCodeAt(i);
    hash |= 0;
  }
  return Math.abs(hash);
}

/**
 * Returns [latitude, longitude] within Chennai for a given consumer record.
 * Prioritizes actual Chennai coordinates; falls back to area & street lookups;
 * applies micro-jitter so multiple meters on the same street remain individually clickable.
 */
export function getConsumerChennaiCoords(consumer) {
  if (!consumer) return CHENNAI_CENTER;
  const cId = consumer.consumer_id || '';
  const hash = hashString(cId);

  // Check if existing lat/lon or latitude/longitude are within Chennai bounds (12.80N to 13.25N, 80.00E to 80.35E)
  const rawLat = consumer.latitude !== undefined ? consumer.latitude : consumer.lat;
  const rawLon = consumer.longitude !== undefined ? consumer.longitude : consumer.lon;
  const lat = typeof rawLat === 'number' ? rawLat : (typeof rawLat === 'string' ? parseFloat(rawLat) : null);
  const lon = typeof rawLon === 'number' ? rawLon : (typeof rawLon === 'string' ? parseFloat(rawLon) : null);

  if (
    lat !== null && !isNaN(lat) &&
    lon !== null && !isNaN(lon) &&
    lat >= 12.80 &&
    lat <= 13.25 &&
    lon >= 80.00 &&
    lon <= 80.35
  ) {
    return [lat, lon];
  }

  const area = (consumer.area || '').trim();
  const street = (consumer.street || '').trim();
  const cleanStr = (s) => (s || '').toLowerCase().replace(/[^a-z0-9]/g, '');
  const cleanArea = cleanStr(area);
  const cleanStreet = cleanStr(street);

  // Try matching Area in Chennai table
  for (const [hoodName, hoodData] of Object.entries(CHENNAI_NEIGHBORHOOD_COORDS)) {
    const cleanHood = cleanStr(hoodName);
    if (cleanArea.includes(cleanHood) || cleanHood.includes(cleanArea)) {
      // Check for street match
      for (const [stName, stCoords] of Object.entries(hoodData.streets)) {
        const cleanSt = cleanStr(stName);
        if (cleanStreet.includes(cleanSt) || cleanSt.includes(cleanStreet)) {
          // Micro-offset for separate meters on same street (~30 to 80 meters)
          const offsetLat = ((hash % 11) - 5) * 0.0004;
          const offsetLon = (((hash >> 3) % 11) - 5) * 0.0004;
          return [Number((stCoords[0] + offsetLat).toFixed(5)), Number((stCoords[1] + offsetLon).toFixed(5))];
        }
      }
      // If no street match, use hood base with offset
      const offsetLat = ((hash % 17) - 8) * 0.0007;
      const offsetLon = (((hash >> 4) % 17) - 8) * 0.0007;
      return [Number((hoodData.base[0] + offsetLat).toFixed(5)), Number((hoodData.base[1] + offsetLon).toFixed(5))];
    }
  }

  // Fallback: Pick a Chennai neighborhood deterministically from pool
  const hoodKeys = Object.keys(CHENNAI_NEIGHBORHOOD_COORDS);
  const selectedHood = CHENNAI_NEIGHBORHOOD_COORDS[hoodKeys[hash % hoodKeys.length]];
  const offsetLat = ((hash % 15) - 7) * 0.0008;
  const offsetLon = (((hash >> 3) % 15) - 7) * 0.0008;
  return [Number((selectedHood.base[0] + offsetLat).toFixed(5)), Number((selectedHood.base[1] + offsetLon).toFixed(5))];
}

/**
 * Returns marker category string:
 * - 'Critical / Inspect Now'
 * - 'High Priority'
 * - 'Medium / Monitor'
 */
export function getMarkerCategory(anomaly) {
  if (
    anomaly.risk_tier === 'CRITICAL' ||
    anomaly.risk_score >= 0.85 ||
    (typeof anomaly.composite_priority === 'number' && anomaly.composite_priority >= 85)
  ) {
    return 'Critical / Inspect Now';
  }
  if (
    anomaly.risk_tier === 'HIGH' ||
    anomaly.risk_score >= 0.70 ||
    (typeof anomaly.composite_priority === 'number' && anomaly.composite_priority >= 70)
  ) {
    return 'High Priority';
  }
  return 'Medium / Monitor';
}

/**
 * Maps queueData to tactical inspection team map entities with authentic Chennai coordinates.
 */
export function getInspectionTeamEntities(queueData = [], anomalies = []) {
  const teamPositions = {
    'SQUAD ALPHA-01': {
      currentAreaStreet: 'Panagal Park Junction, Usman Road, T. Nagar',
      coords: [13.0402, 80.2365]
    },
    'SQUAD DELTA-04': {
      currentAreaStreet: 'Kathipara Junction, Anna Salai, Guindy',
      coords: [13.0085, 80.2052]
    },
    'SQUAD BRAVO-02': {
      currentAreaStreet: 'Anna Nagar Substation, 2nd Avenue, Anna Nagar',
      coords: [13.0872, 80.2125]
    },
    'SQUAD GAMMA-03': {
      currentAreaStreet: 'Nandanam Substation, Anna Salai',
      coords: [13.0315, 80.2410]
    }
  };

  const seenTeams = new Set();
  const teams = [];

  for (const q of queueData) {
    if (seenTeams.has(q.team)) continue;
    seenTeams.add(q.team);

    const anomaly = anomalies.find(a => a.consumer_id === q.consumer_id) || anomalies[0];
    const consumerName = anomaly ? (anomaly.consumer_name || anomaly.consumer_id) : q.consumer_id;
    const destArea = anomaly ? `${anomaly.street || ''}, ${anomaly.area || ''}`.trim() : 'Chennai Grid Substation';

    const defaultPos = teamPositions[q.team] || {
      currentAreaStreet: `${destArea} (En-Route Patrol)`,
      coords: [13.0450 + (teams.length * 0.015), 80.2200 + (teams.length * 0.015)]
    };

    teams.push({
      teamName: q.team,
      currentAreaStreet: defaultPos.currentAreaStreet,
      assignedConsumer: `${consumerName} (${q.consumer_id})`,
      destination: destArea,
      status: q.status || 'SCHEDULED',
      coords: defaultPos.coords
    });
  }

  return teams;
}
