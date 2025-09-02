from agents import function_tool, Tool

class RequirementTools:
    @classmethod
    @function_tool
    async def research_domain_standards(cls, domain: str) -> Tool:
        """
        Research the domain standards for the given domain
        """
        # Common domain standards mapping
        domain_standards = {
            "healthcare": {
                "standards": ["HIPAA", "HL7 FHIR", "DICOM", "ISO 27001"],
                "description": "Healthcare data privacy, interoperability, and security standards"
            },
            "finance": {
                "standards": ["PCI DSS", "SOX", "Basel III", "ISO 20022"],
                "description": "Financial data security, compliance, and transaction standards"
            },
            "education": {
                "standards": ["FERPA", "COPPA", "SCORM", "xAPI"],
                "description": "Student privacy, child protection, and learning technology standards"
            },
            "ecommerce": {
                "standards": ["PCI DSS", "GDPR", "WCAG", "ISO 27001"],
                "description": "Payment security, data protection, accessibility, and information security"
            },
            "manufacturing": {
                "standards": ["ISO 9001", "ISO 14001", "IATF 16949", "AS9100"],
                "description": "Quality management, environmental, automotive, and aerospace standards"
            }
        }

        domain_name = domain.lower().strip()
        if domain_name in domain_standards:
            standards_info = domain_standards[domain_name]
            result = f"Domain: {domain.title()}\n"
            result += f"Description: {standards_info['description']}\n"
            result += f"Key Standards: {', '.join(standards_info['standards'])}\n"
            return result
        
        # Partial matching domain.
        matching_domains = []
        for key, value in domain_standards.items():
            if key in domain_name or domain_name in key:
                matching_domains.append((key, value))
        
        if matching_domains:
            result = f"Domain: {domain.title()}\n"
            result += f"Description: {matching_domains[0][1]['description']}\n"
            result += f"Key Standards: {', '.join(matching_domains[0][1]['standards'])}\n"
            return result

        return f"No matching domain standards found for {domain.title()}"

    @classmethod
    @function_tool
    async def research_domain_laws(cls) -> Tool:
        """
        Research the domain laws for the given domain
        """
        pass
    
    @classmethod
    @function_tool
    async def research_domain_regulations(cls) -> Tool:
        """
        Research the domain regulations for the given domain
        """
        pass