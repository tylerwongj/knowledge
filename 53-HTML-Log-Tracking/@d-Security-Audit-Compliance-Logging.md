# @d-Security Audit & Compliance Logging

## 🎯 Learning Objectives
- Implement security-focused logging for compliance and audit requirements
- Create tamper-proof log systems with cryptographic verification
- Design automated security monitoring and threat detection workflows
- Build compliance reporting systems for various regulatory frameworks

## 🔧 Security Logging Implementation

### Secure Log Entry Structure
```javascript
class SecureLogTracker {
  constructor(options = {}) {
    this.encryptionKey = options.encryptionKey || this.generateEncryptionKey();
    this.signingKey = options.signingKey || this.generateSigningKey();
    this.logs = [];
    this.auditTrail = new Map();
    this.complianceConfig = options.compliance || {};
    
    this.initializeSecureLogging();
  }

  async createSecureLogEntry(level, message, context = {}) {
    const baseEntry = {
      id: this.generateSecureId(),
      timestamp: new Date().toISOString(),
      level: level,
      message: message,
      context: this.sanitizeContext(context),
      sessionId: this.getSecureSessionId(),
      userId: this.getCurrentUserId(),
      ipAddress: this.getClientIP(),
      userAgent: navigator.userAgent,
      url: window.location.href,
      referrer: document.referrer
    };

    // Add security-specific metadata
    const securityMetadata = {
      integrity: await this.calculateIntegrity(baseEntry),
      signature: await this.signLogEntry(baseEntry),
      encryptedFields: await this.encryptSensitiveData(baseEntry),
      compliance: this.addComplianceMetadata(baseEntry)
    };

    const secureEntry = {
      ...baseEntry,
      security: securityMetadata,
      auditChain: this.buildAuditChain()
    };

    this.logs.push(secureEntry);
    this.updateAuditTrail(secureEntry);
    
    // Check for security events
    await this.analyzeSecurityImplications(secureEntry);
    
    return secureEntry;
  }

  async calculateIntegrity(entry) {
    const entryString = JSON.stringify(entry, Object.keys(entry).sort());
    const encoder = new TextEncoder();
    const data = encoder.encode(entryString);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    return Array.from(new Uint8Array(hashBuffer))
      .map(b => b.toString(16).padStart(2, '0'))
      .join('');
  }

  async signLogEntry(entry) {
    const entryData = new TextEncoder().encode(JSON.stringify(entry));
    const signature = await crypto.subtle.sign(
      'HMAC',
      this.signingKey,
      entryData
    );
    return Array.from(new Uint8Array(signature))
      .map(b => b.toString(16).padStart(2, '0'))
      .join('');
  }

  async encryptSensitiveData(entry) {
    const sensitiveFields = ['userId', 'ipAddress', 'sessionId'];
    const encrypted = {};

    for (const field of sensitiveFields) {
      if (entry[field]) {
        encrypted[field] = await this.encryptField(entry[field]);
      }
    }

    return encrypted;
  }

  sanitizeContext(context) {
    const sanitized = { ...context };
    
    // Remove sensitive data patterns
    const sensitivePatterns = [
      /password/i,
      /secret/i,
      /token/i,
      /key/i,
      /ssn/i,
      /credit/i,
      /card/i
    ];

    for (const [key, value] of Object.entries(sanitized)) {
      if (sensitivePatterns.some(pattern => pattern.test(key))) {
        sanitized[key] = '[REDACTED]';
      } else if (typeof value === 'string' && this.containsSensitiveData(value)) {
        sanitized[key] = this.maskSensitiveData(value);
      }
    }

    return sanitized;
  }

  addComplianceMetadata(entry) {
    const metadata = {
      gdpr: this.addGDPRMetadata(entry),
      hipaa: this.addHIPAAMetadata(entry),
      sox: this.addSOXMetadata(entry),
      pci: this.addPCIMetadata(entry)
    };

    return metadata;
  }

  addGDPRMetadata(entry) {
    return {
      dataSubject: this.identifyDataSubject(entry),
      legalBasis: this.determineLegalBasis(entry),
      dataCategories: this.categorizePersonalData(entry),
      retention: this.calculateRetentionPeriod(entry),
      rightToErasure: this.assessErasureRights(entry)
    };
  }

  addHIPAAMetadata(entry) {
    return {
      phi: this.identifyPHI(entry),
      minimumNecessary: this.validateMinimumNecessary(entry),
      authorization: this.checkAuthorization(entry),
      auditRequired: this.isAuditRequired(entry)
    };
  }
}
```

### Security Event Detection
```javascript
class SecurityEventDetector {
  constructor(logTracker) {
    this.logTracker = logTracker;
    this.threatIntelligence = new Map();
    this.securityRules = [];
    this.alerts = [];
    
    this.initializeSecurityRules();
  }

  initializeSecurityRules() {
    this.securityRules = [
      {
        id: 'failed-login-attempts',
        pattern: /authentication.*failed/i,
        threshold: 5,
        timeWindow: 300000, // 5 minutes
        severity: 'high',
        action: 'block-ip'
      },
      {
        id: 'sql-injection-attempt',
        pattern: /(union|select|insert|update|delete|drop|create|alter).*[\'"]/i,
        threshold: 1,
        timeWindow: 0,
        severity: 'critical',
        action: 'immediate-alert'
      },
      {
        id: 'xss-attempt',
        pattern: /<script|javascript:|on\w+\s*=/i,
        threshold: 1,
        timeWindow: 0,
        severity: 'high',
        action: 'sanitize-and-alert'
      },
      {
        id: 'suspicious-file-access',
        pattern: /\.\.(\/|\\)|system32|passwd|shadow/i,
        threshold: 1,
        timeWindow: 0,
        severity: 'critical',
        action: 'block-request'
      },
      {
        id: 'rate-limiting-violation',
        pattern: /rate.limit.exceeded/i,
        threshold: 10,
        timeWindow: 60000, // 1 minute
        severity: 'medium',
        action: 'throttle-user'
      }
    ];
  }

  async analyzeLogForThreats(logEntry) {
    const threats = [];

    for (const rule of this.securityRules) {
      if (this.matchesSecurityRule(logEntry, rule)) {
        const threat = await this.createThreatEvent(logEntry, rule);
        threats.push(threat);
        
        if (rule.action === 'immediate-alert') {
          await this.triggerImmediateAlert(threat);
        }
      }
    }

    return threats;
  }

  matchesSecurityRule(logEntry, rule) {
    const searchText = `${logEntry.message} ${JSON.stringify(logEntry.context)}`;
    return rule.pattern.test(searchText);
  }

  async createThreatEvent(logEntry, rule) {
    const threat = {
      id: this.generateThreatId(),
      timestamp: new Date().toISOString(),
      ruleId: rule.id,
      severity: rule.severity,
      sourceEntry: logEntry.id,
      description: this.generateThreatDescription(logEntry, rule),
      indicators: this.extractThreatIndicators(logEntry, rule),
      riskScore: await this.calculateRiskScore(logEntry, rule),
      mitigation: this.suggestMitigation(rule),
      complianceImpact: this.assessComplianceImpact(logEntry, rule)
    };

    this.logSecurityEvent(threat);
    return threat;
  }

  async calculateRiskScore(logEntry, rule) {
    let baseScore = this.getSeverityScore(rule.severity);
    
    // Adjust based on user context
    if (logEntry.userId && await this.isPrivilegedUser(logEntry.userId)) {
      baseScore += 2;
    }

    // Adjust based on IP reputation
    const ipReputation = await this.checkIPReputation(logEntry.ipAddress);
    baseScore += ipReputation.riskAdjustment;

    // Adjust based on frequency
    const frequency = this.getEventFrequency(rule.id, logEntry.ipAddress);
    baseScore += Math.min(frequency * 0.5, 3);

    return Math.min(baseScore, 10);
  }

  extractThreatIndicators(logEntry, rule) {
    const indicators = {
      iocs: [], // Indicators of Compromise
      tactics: [], // MITRE ATT&CK tactics
      techniques: [] // MITRE ATT&CK techniques
    };

    switch (rule.id) {
      case 'sql-injection-attempt':
        indicators.tactics.push('Initial Access', 'Execution');
        indicators.techniques.push('T1190 - Exploit Public-Facing Application');
        indicators.iocs.push({
          type: 'payload',
          value: this.extractSQLPayload(logEntry.message)
        });
        break;

      case 'xss-attempt':
        indicators.tactics.push('Initial Access', 'Execution');
        indicators.techniques.push('T1566 - Phishing');
        indicators.iocs.push({
          type: 'script',
          value: this.extractXSSPayload(logEntry.message)
        });
        break;

      case 'failed-login-attempts':
        indicators.tactics.push('Credential Access');
        indicators.techniques.push('T1110 - Brute Force');
        break;
    }

    return indicators;
  }
}
```

### Compliance Reporting Engine
```javascript
class ComplianceReporter {
  constructor(logTracker, config = {}) {
    this.logTracker = logTracker;
    this.config = config;
    this.reportTemplates = new Map();
    this.scheduledReports = [];
    
    this.initializeReportTemplates();
  }

  initializeReportTemplates() {
    // GDPR Article 30 Record of Processing Activities
    this.reportTemplates.set('gdpr-article-30', {
      title: 'GDPR Article 30 - Record of Processing Activities',
      sections: [
        'data-controller-details',
        'processing-purposes',
        'data-categories',
        'data-recipients',
        'data-transfers',
        'retention-periods',
        'security-measures'
      ],
      frequency: 'annual',
      compliance: 'gdpr'
    });

    // HIPAA Security Rule Audit
    this.reportTemplates.set('hipaa-security-audit', {
      title: 'HIPAA Security Rule Compliance Audit',
      sections: [
        'access-controls',
        'audit-logs',
        'integrity-controls',
        'transmission-security',
        'incident-response'
      ],
      frequency: 'quarterly',
      compliance: 'hipaa'
    });

    // SOX IT Controls Report
    this.reportTemplates.set('sox-it-controls', {
      title: 'SOX IT General Controls Report',
      sections: [
        'access-management',
        'change-management',
        'data-backup-recovery',
        'system-monitoring',
        'incident-management'
      ],
      frequency: 'quarterly',
      compliance: 'sox'
    });
  }

  async generateComplianceReport(templateId, dateRange) {
    const template = this.reportTemplates.get(templateId);
    if (!template) {
      throw new Error(`Unknown report template: ${templateId}`);
    }

    const relevantLogs = this.filterLogsByCompliance(
      template.compliance, 
      dateRange
    );

    const report = {
      id: this.generateReportId(),
      title: template.title,
      compliance: template.compliance,
      period: dateRange,
      generatedAt: new Date().toISOString(),
      sections: await this.generateReportSections(template.sections, relevantLogs),
      summary: await this.generateExecutiveSummary(relevantLogs, template),
      recommendations: await this.generateComplianceRecommendations(relevantLogs, template),
      attestation: this.generateAttestation()
    };

    return report;
  }

  async generateReportSections(sectionIds, logs) {
    const sections = {};

    for (const sectionId of sectionIds) {
      sections[sectionId] = await this.generateReportSection(sectionId, logs);
    }

    return sections;
  }

  async generateReportSection(sectionId, logs) {
    switch (sectionId) {
      case 'access-controls':
        return this.generateAccessControlsSection(logs);
      
      case 'audit-logs':
        return this.generateAuditLogsSection(logs);
      
      case 'data-categories':
        return this.generateDataCategoriesSection(logs);
      
      case 'security-measures':
        return this.generateSecurityMeasuresSection(logs);
      
      default:
        return { error: `Unknown section: ${sectionId}` };
    }
  }

  generateAccessControlsSection(logs) {
    const accessLogs = logs.filter(log => 
      log.context.action && 
      ['login', 'logout', 'access', 'permission'].some(keyword => 
        log.context.action.toLowerCase().includes(keyword)
      )
    );

    return {
      title: 'Access Controls Review',
      summary: `Analyzed ${accessLogs.length} access-related events`,
      findings: {
        successfulAccess: accessLogs.filter(log => log.level === 'info').length,
        failedAccess: accessLogs.filter(log => log.level === 'error').length,
        privilegedAccess: accessLogs.filter(log => 
          log.context.privileged === true
        ).length
      },
      issues: this.identifyAccessControlIssues(accessLogs),
      recommendations: this.generateAccessControlRecommendations(accessLogs)
    };
  }

  async scheduleComplianceReport(templateId, schedule) {
    const scheduledReport = {
      id: this.generateScheduleId(),
      templateId: templateId,
      schedule: schedule, // cron expression
      lastRun: null,
      nextRun: this.calculateNextRun(schedule),
      enabled: true
    };

    this.scheduledReports.push(scheduledReport);
    this.setupReportScheduler(scheduledReport);
    
    return scheduledReport;
  }

  async exportReport(report, format = 'pdf') {
    switch (format) {
      case 'pdf':
        return await this.generatePDFReport(report);
      
      case 'html':
        return this.generateHTMLReport(report);
      
      case 'json':
        return JSON.stringify(report, null, 2);
      
      case 'csv':
        return this.convertReportToCSV(report);
      
      default:
        throw new Error(`Unsupported export format: ${format}`);
    }
  }
}
```

### Automated Compliance Monitoring
```javascript
class ComplianceMonitor {
  constructor(logTracker, complianceConfig) {
    this.logTracker = logTracker;
    this.config = complianceConfig;
    this.violations = [];
    this.monitoringRules = [];
    
    this.initializeMonitoringRules();
    this.startContinuousMonitoring();
  }

  initializeMonitoringRules() {
    // GDPR monitoring rules
    if (this.config.gdpr?.enabled) {
      this.monitoringRules.push({
        id: 'gdpr-data-retention',
        compliance: 'gdpr',
        check: this.checkDataRetentionCompliance.bind(this),
        frequency: 'daily',
        severity: 'high'
      });

      this.monitoringRules.push({
        id: 'gdpr-consent-tracking',
        compliance: 'gdpr',
        check: this.checkConsentTracking.bind(this),
        frequency: 'realtime',
        severity: 'critical'
      });
    }

    // HIPAA monitoring rules
    if (this.config.hipaa?.enabled) {
      this.monitoringRules.push({
        id: 'hipaa-access-logging',
        compliance: 'hipaa',
        check: this.checkHIPAAAccessLogging.bind(this),
        frequency: 'hourly',
        severity: 'critical'
      });

      this.monitoringRules.push({
        id: 'hipaa-minimum-necessary',
        compliance: 'hipaa',
        check: this.checkMinimumNecessaryRule.bind(this),
        frequency: 'realtime',
        severity: 'high'
      });
    }
  }

  async checkDataRetentionCompliance() {
    const retentionPolicies = this.config.gdpr.retentionPolicies;
    const violations = [];

    for (const [dataType, policy] of Object.entries(retentionPolicies)) {
      const expiredData = await this.findExpiredData(dataType, policy.maxAge);
      
      if (expiredData.length > 0) {
        violations.push({
          type: 'data-retention-violation',
          compliance: 'gdpr',
          dataType: dataType,
          expiredRecords: expiredData.length,
          action: 'automatic-deletion-required',
          deadline: this.calculateDeletionDeadline(policy)
        });
      }
    }

    return violations;
  }

  async checkConsentTracking(logEntry) {
    if (!this.involvesPersonalData(logEntry)) {
      return [];
    }

    const userId = logEntry.userId;
    const consentRecord = await this.getConsentRecord(userId);
    
    if (!consentRecord || !this.isConsentValid(consentRecord)) {
      return [{
        type: 'gdpr-consent-violation',
        compliance: 'gdpr',
        userId: userId,
        violation: 'processing-without-valid-consent',
        severity: 'critical',
        action: 'halt-processing'
      }];
    }

    return [];
  }

  async generateComplianceScore() {
    const scores = {
      gdpr: await this.calculateGDPRScore(),
      hipaa: await this.calculateHIPAAScore(),
      sox: await this.calculateSOXScore(),
      overall: 0
    };

    scores.overall = Object.values(scores)
      .filter(score => typeof score === 'number')
      .reduce((sum, score) => sum + score, 0) / 
      Object.keys(scores).length;

    return scores;
  }

  async calculateGDPRScore() {
    const checks = [
      { name: 'consent-tracking', weight: 0.3, score: await this.assessConsentTracking() },
      { name: 'data-retention', weight: 0.25, score: await this.assessDataRetention() },
      { name: 'right-to-erasure', weight: 0.2, score: await this.assessRightToErasure() },
      { name: 'data-minimization', weight: 0.15, score: await this.assessDataMinimization() },
      { name: 'security-measures', weight: 0.1, score: await this.assessSecurityMeasures() }
    ];

    return checks.reduce((total, check) => 
      total + (check.score * check.weight), 0
    ) * 100;
  }
}
```

## 🚀 AI/LLM Integration Opportunities

### Intelligent Compliance Analysis
```javascript
class AIComplianceAnalyzer {
  async analyzeComplianceGaps(logs, regulations) {
    const prompt = `
      Analyze these security logs for compliance gaps:
      
      Regulations: ${regulations.join(', ')}
      Recent logs: ${JSON.stringify(logs.slice(-200), null, 2)}
      
      Identify:
      1. Potential compliance violations
      2. Missing required audit trails
      3. Data retention policy violations
      4. Access control weaknesses
      5. Recommended remediation actions
      
      Provide specific citations to relevant regulations.
    `;

    return await this.sendToAI(prompt);
  }

  async generateComplianceStrategy(currentState, targetCompliance) {
    const prompt = `
      Create a compliance implementation strategy:
      
      Current state: ${JSON.stringify(currentState)}
      Target compliance: ${targetCompliance}
      
      Provide:
      1. Gap analysis with priorities
      2. Implementation roadmap with timelines
      3. Resource requirements
      4. Risk assessment
      5. Success metrics
      6. Ongoing monitoring strategy
    `;

    return await this.sendToAI(prompt);
  }
}
```

## 💡 Key Highlights

### Security Logging Essentials
- **Tamper-Proof Logs**: Cryptographic signatures and integrity verification
- **Compliance Metadata**: Automatic tagging for GDPR, HIPAA, SOX requirements
- **Threat Detection**: Real-time security event analysis and alerting
- **Data Sanitization**: Automatic removal of sensitive information
- **Audit Trails**: Complete chain of custody for all log entries

### Unity Security Applications
- **Player Data Protection**: Secure logging of user interactions and data
- **Anti-Cheat Monitoring**: Detect and log suspicious player behavior
- **Asset Protection**: Monitor unauthorized access to game assets
- **Build Security**: Track Unity build processes and deployment security
- **Multiplayer Security**: Log network events and potential exploits

### Compliance Framework Support
- **GDPR**: Right to erasure, consent tracking, data minimization
- **HIPAA**: PHI protection, minimum necessary rule, audit logs
- **SOX**: IT general controls, change management, access controls
- **PCI DSS**: Payment data protection, security monitoring
- **ISO 27001**: Information security management systems

### Career Development Value
- **Security Engineering**: Demonstrate advanced security logging capabilities
- **Compliance Expertise**: Show understanding of regulatory requirements
- **Risk Management**: Display ability to identify and mitigate security risks
- **Audit Preparation**: Showcase skills in preparing for compliance audits
- **Enterprise Security**: Highlight enterprise-grade security implementation skills