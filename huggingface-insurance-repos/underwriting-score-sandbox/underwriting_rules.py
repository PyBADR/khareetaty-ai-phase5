"""
Underwriting Risk Scoring Rules Engine
100% rule-based, no ML, synthetic only
"""

class UnderwritingScorer:
    """Rule-based underwriting risk scorer"""
    
    def __init__(self):
        # Industry risk factors (0.0 - 1.0)
        self.industry_risk_factors = {
            'Technology': 0.1,
            'Professional Services': 0.15,
            'Education': 0.15,
            'Retail': 0.25,
            'Healthcare': 0.30,
            'Hospitality': 0.35,
            'Manufacturing': 0.50,
            'Transportation': 0.60,
            'Construction': 0.75
        }
    
    def calculate_industry_factor(self, industry_segment):
        """Calculate risk factor from industry"""
        return self.industry_risk_factors.get(industry_segment, 0.30)
    
    def calculate_history_factor(self, prior_claim_count):
        """Calculate risk factor from claim history"""
        if prior_claim_count == 0:
            return 0.0
        elif prior_claim_count <= 2:
            return 0.15
        elif prior_claim_count <= 4:
            return 0.35
        elif prior_claim_count <= 6:
            return 0.60
        else:
            return 0.85
    
    def calculate_profile_factor(self, applicant_risk_profile):
        """Calculate risk factor from applicant profile"""
        profile_factors = {
            'Low': 0.0,
            'Medium': 0.30,
            'High': 0.70
        }
        return profile_factors.get(applicant_risk_profile, 0.30)
    
    def calculate_aggregate_score(self, industry_factor, history_factor, profile_factor):
        """Aggregate risk factors with weights"""
        aggregate = (
            industry_factor * 0.40 +  # Industry weight: 40%
            history_factor * 0.35 +   # History weight: 35%
            profile_factor * 0.25      # Profile weight: 25%
        )
        return min(aggregate, 1.0)
    
    def determine_risk_band(self, aggregate_score):
        """Map aggregate score to risk band"""
        if aggregate_score < 0.30:
            return 'Low'
        elif aggregate_score < 0.60:
            return 'Medium'
        else:
            return 'High'
    
    def score_applicant(self, industry_segment, applicant_risk_profile, prior_claim_count):
        """
        Main scoring function
        
        Args:
            industry_segment: Industry category
            applicant_risk_profile: Low/Medium/High
            prior_claim_count: Number of prior claims (0-10)
        
        Returns:
            dict with risk_band, aggregate_score, factor breakdown, and explanation
        """
        # Calculate individual factors
        industry_factor = self.calculate_industry_factor(industry_segment)
        history_factor = self.calculate_history_factor(prior_claim_count)
        profile_factor = self.calculate_profile_factor(applicant_risk_profile)
        
        # Calculate aggregate score
        aggregate_score = self.calculate_aggregate_score(
            industry_factor, history_factor, profile_factor
        )
        
        # Determine risk band
        risk_band = self.determine_risk_band(aggregate_score)
        
        # Build factor breakdown
        factor_breakdown = {
            'industry_factor': round(industry_factor, 3),
            'history_factor': round(history_factor, 3),
            'profile_factor': round(profile_factor, 3),
            'aggregate_score': round(aggregate_score, 3)
        }
        
        # Build explanation
        explanation = self._build_explanation(
            industry_segment, applicant_risk_profile, prior_claim_count,
            industry_factor, history_factor, profile_factor, risk_band
        )
        
        return {
            'risk_band': risk_band,
            'aggregate_score': round(aggregate_score, 3),
            'factor_breakdown': factor_breakdown,
            'explanation': explanation,
            'underwriter_review_required': True  # Always required
        }
    
    def _build_explanation(self, industry, profile, claims, 
                          ind_factor, hist_factor, prof_factor, band):
        """Build human-readable explanation"""
        explanation = f"### Risk Assessment: {band}\n\n"
        explanation += f"**Aggregate Risk Score:** {self.calculate_aggregate_score(ind_factor, hist_factor, prof_factor):.3f} / 1.000\n\n"
        
        explanation += "**Factor Breakdown:**\n\n"
        
        # Industry factor
        if ind_factor < 0.30:
            ind_desc = "Low-risk industry sector"
        elif ind_factor < 0.50:
            ind_desc = "Moderate-risk industry sector"
        else:
            ind_desc = "High-risk industry sector"
        explanation += f"- **Industry ({industry}):** {ind_factor:.3f} - {ind_desc}\n"
        
        # History factor
        if claims == 0:
            hist_desc = "No prior claims (excellent)"
        elif claims <= 2:
            hist_desc = "Minimal claim history (good)"
        elif claims <= 4:
            hist_desc = "Moderate claim frequency (concerning)"
        else:
            hist_desc = f"Excessive claim frequency ({claims} claims)"
        explanation += f"- **Claim History:** {hist_factor:.3f} - {hist_desc}\n"
        
        # Profile factor
        explanation += f"- **Applicant Profile ({profile}):** {prof_factor:.3f}\n\n"
        
        # Band recommendation
        explanation += "**Recommendation:**\n\n"
        if band == 'Low':
            explanation += "✅ Standard underwriting process may proceed. "
            explanation += "Minimal additional documentation required.\n"
        elif band == 'Medium':
            explanation += "⚠️ Enhanced underwriting review recommended. "
            explanation += "Request additional documentation and risk mitigation measures.\n"
        else:
            explanation += "🚨 High-risk applicant requiring detailed underwriting assessment. "
            explanation += "Consider risk controls, higher deductibles, or coverage limitations.\n"
        
        explanation += "\n---\n\n"
        explanation += "⚠️ **MANDATORY: Underwriter review and approval required before binding coverage.**\n"
        explanation += "This is an advisory tool only. Final underwriting decisions must be made by qualified underwriters."
        
        return explanation
