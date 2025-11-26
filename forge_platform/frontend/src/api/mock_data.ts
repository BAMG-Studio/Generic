export interface AuditFile {
  id: string;
  path: string;
  name: string;
  size_kb: number;
  classification: 'foreground' | 'third_party' | 'background';
  confidence: number; // 0.0 - 1.0
  license: string | null;
  risk_score: number; // 0 - 100
  features: {
    template_indicator: number;
    language_entropy: number;
    external_import_ratio: number;
  };
}

export const MOCK_REPO_STATS = {
  repo_name: "forge-trace-core",
  scan_date: "2025-11-20T18:30:00Z",
  total_files: 1240,
  ip_split: {
    foreground: 65,   // 65% Proprietary
    third_party: 25,  // 25% Open Source
    background: 10    // 10% Vendor/Legacy
  },
  rewrite_cost_estimate: "$45,000", // Estimate to replace background code
  overall_risk: "Medium", // Driven by that one GPL file below
};

export const MOCK_FILES: AuditFile[] = [
  // Scenario 1: High Confidence Foreground (Your core logic)
  {
    id: "f1",
    path: "src/engine/analyzer.py",
    name: "analyzer.py",
    size_kb: 14.2,
    classification: "foreground",
    confidence: 0.99,
    license: "Proprietary",
    risk_score: 0,
    features: {
      template_indicator: 0.01,
      language_entropy: 5.2, // High entropy = complex human logic
      external_import_ratio: 0.1
    }
  },
  
  // Scenario 2: Obvious Third Party (Standard Library)
  {
    id: "f2",
    path: "src/utils/lodash_custom.js",
    name: "lodash_custom.js",
    size_kb: 85.0,
    classification: "third_party",
    confidence: 0.98,
    license: "MIT",
    risk_score: 10,
    features: {
      template_indicator: 0.05,
      language_entropy: 4.1,
      external_import_ratio: 0.0
    }
  },

  // Scenario 3: The "Review Queue" Candidate (Low Confidence)
  // ForgeTrace isn't sure if this is vendor code or yours.
  {
    id: "f3",
    path: "src/legacy/payment_gateway_v1.php",
    name: "payment_gateway_v1.php",
    size_kb: 45.5,
    classification: "background",
    confidence: 0.68, // < 0.7 Threshold! Should trigger UI alert.
    license: "Unknown",
    risk_score: 45,
    features: {
      template_indicator: 0.4, // Somewhat looks generated
      language_entropy: 3.8,
      external_import_ratio: 0.3
    }
  },

  // Scenario 4: High Risk! (GPL Infection)
  {
    id: "f4",
    path: "lib/gpl_snippet.c",
    name: "gpl_snippet.c",
    size_kb: 12.0,
    classification: "third_party",
    confidence: 0.95,
    license: "GPL-3.0", // DANGER
    risk_score: 95, // UI should color this bright red
    features: {
      template_indicator: 0.1,
      language_entropy: 4.5,
      external_import_ratio: 0.0
    }
  }
];
