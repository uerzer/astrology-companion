"""
Natal Chart Backend Service
Wraps the Kerykeion skill with clean API for the Gradio frontend
"""

from kerykeion import AstrologicalSubject, KerykeionChartSVG, NatalAspects
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import json
from pathlib import Path


class NatalChartGenerator:
    """Clean API wrapper for natal chart generation"""
    
    def __init__(self):
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_chart(
        self,
        name: str,
        year: int,
        month: int,
        day: int,
        hour: int,
        minute: int,
        latitude: float,
        longitude: float,
        timezone: str,
        city: Optional[str] = None
    ) -> Dict:
        """
        Generate complete natal chart with interpretations
        
        Returns:
            Dict with keys: subject_data, chart_svg_path, interpretation, aspects
        """
        try:
            # Create astrological subject
            subject = AstrologicalSubject(
                name=name,
                year=year,
                month=month,
                day=day,
                hour=hour,
                minute=minute,
                lat=latitude,
                lng=longitude,
                tz_str=timezone
            )
            
            # Generate SVG chart
            chart = KerykeionChartSVG(subject)
            svg_path = self.output_dir / f"{name.replace(' ', '_')}_chart.svg"
            chart.makeSVG()
            
            # Get aspects
            aspects = NatalAspects(subject)
            
            # Extract key data
            chart_data = {
                "success": True,
                "name": name,
                "birth_data": {
                    "date": f"{year}-{month:02d}-{day:02d}",
                    "time": f"{hour:02d}:{minute:02d}",
                    "city": city or "Unknown",
                    "latitude": latitude,
                    "longitude": longitude,
                    "timezone": timezone
                },
                "placements": self._extract_placements(subject),
                "aspects": self._extract_aspects(aspects),
                "houses": self._extract_houses(subject),
                "chart_svg_path": str(svg_path),
                "interpretation": self._generate_interpretation(subject)
            }
            
            return chart_data
            
        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }
    
    def _extract_placements(self, subject: AstrologicalSubject) -> List[Dict]:
        """Extract planetary placements"""
        placements = []
        
        # Main planets to include
        planets = [
            ('sun', 'Sun'),
            ('moon', 'Moon'),
            ('mercury', 'Mercury'),
            ('venus', 'Venus'),
            ('mars', 'Mars'),
            ('jupiter', 'Jupiter'),
            ('saturn', 'Saturn'),
            ('uranus', 'Uranus'),
            ('neptune', 'Neptune'),
            ('pluto', 'Pluto'),
            ('mean_node', 'North Node')
        ]
        
        for attr_name, planet_name in planets:
            if hasattr(subject, attr_name):
                planet_obj = getattr(subject, attr_name)
                placements.append({
                    "planet": planet_name,
                    "sign": planet_obj.get('sign', 'Unknown'),
                    "position": planet_obj.get('position', 0),
                    "house": planet_obj.get('house', 'Unknown'),
                    "retrograde": planet_obj.get('retrograde', False)
                })
        
        # Add Rising Sign (Ascendant)
        if hasattr(subject, 'first_house'):
            placements.insert(0, {
                "planet": "Ascendant (Rising)",
                "sign": subject.first_house.get('sign', 'Unknown'),
                "position": subject.first_house.get('position', 0),
                "house": "1",
                "retrograde": False
            })
        
        return placements
    
    def _extract_aspects(self, aspects: NatalAspects) -> List[Dict]:
        """Extract major aspects"""
        aspect_list = []
        
        if hasattr(aspects, 'all_aspects'):
            for aspect in aspects.all_aspects:
                aspect_list.append({
                    "planet1": aspect.get('p1_name', 'Unknown'),
                    "planet2": aspect.get('p2_name', 'Unknown'),
                    "aspect_type": aspect.get('aspect', 'Unknown'),
                    "orb": aspect.get('orbit', 0),
                    "aspect_degrees": aspect.get('aspect_degrees', 0)
                })
        
        return aspect_list
    
    def _extract_houses(self, subject: AstrologicalSubject) -> List[Dict]:
        """Extract house cusps"""
        houses = []
        
        for i in range(1, 13):
            house_attr = f"house{i}" if i > 1 else "first_house"
            if hasattr(subject, house_attr):
                house_obj = getattr(subject, house_attr)
                houses.append({
                    "house": i,
                    "sign": house_obj.get('sign', 'Unknown'),
                    "position": house_obj.get('position', 0)
                })
        
        return houses
    
    def _generate_interpretation(self, subject: AstrologicalSubject) -> Dict:
        """Generate basic interpretations for key placements"""
        interpretations = {}
        
        # Sun sign interpretation
        if hasattr(subject, 'sun'):
            sun_sign = subject.sun.get('sign', '')
            interpretations['sun'] = self._interpret_sun(sun_sign)
        
        # Moon sign interpretation
        if hasattr(subject, 'moon'):
            moon_sign = subject.moon.get('sign', '')
            interpretations['moon'] = self._interpret_moon(moon_sign)
        
        # Rising sign interpretation
        if hasattr(subject, 'first_house'):
            rising_sign = subject.first_house.get('sign', '')
            interpretations['rising'] = self._interpret_rising(rising_sign)
        
        return interpretations
    
    def _interpret_sun(self, sign: str) -> str:
        """Quick Sun sign interpretation"""
        interpretations = {
            "Aries": "Bold, pioneering, and action-oriented. You lead with courage and initiative.",
            "Taurus": "Grounded, patient, and values-driven. You seek stability and sensory pleasure.",
            "Gemini": "Curious, communicative, and adaptable. You thrive on variety and mental stimulation.",
            "Cancer": "Nurturing, intuitive, and emotionally deep. You value home and emotional security.",
            "Leo": "Confident, creative, and expressive. You shine through self-expression and generosity.",
            "Virgo": "Analytical, practical, and service-oriented. You excel through precision and helpfulness.",
            "Libra": "Diplomatic, harmonious, and relationship-focused. You seek balance and beauty.",
            "Scorpio": "Intense, transformative, and emotionally powerful. You dive deep and transform.",
            "Sagittarius": "Adventurous, philosophical, and optimistic. You seek meaning and expansion.",
            "Capricorn": "Ambitious, disciplined, and achievement-oriented. You build lasting structures.",
            "Aquarius": "Innovative, humanitarian, and individualistic. You envision progressive futures.",
            "Pisces": "Compassionate, imaginative, and spiritually attuned. You dissolve boundaries."
        }
        return interpretations.get(sign, "Core identity and life force expression.")
    
    def _interpret_moon(self, sign: str) -> str:
        """Quick Moon sign interpretation"""
        interpretations = {
            "Aries": "Emotional courage and quick feelings. You need independence and action.",
            "Taurus": "Emotional stability and comfort-seeking. You need security and sensory ease.",
            "Gemini": "Emotionally curious and communicative. You need variety and mental connection.",
            "Cancer": "Deeply nurturing and protective. You need emotional safety and family bonds.",
            "Leo": "Emotionally warm and expressive. You need recognition and creative outlets.",
            "Virgo": "Emotionally practical and analytical. You need order and useful service.",
            "Libra": "Emotionally balanced and relational. You need harmony and partnership.",
            "Scorpio": "Emotionally intense and private. You need depth and transformative connection.",
            "Sagittarius": "Emotionally optimistic and free. You need adventure and philosophical meaning.",
            "Capricorn": "Emotionally controlled and responsible. You need structure and achievement.",
            "Aquarius": "Emotionally detached and humanitarian. You need freedom and intellectual stimulation.",
            "Pisces": "Emotionally empathic and boundless. You need spiritual connection and creativity."
        }
        return interpretations.get(sign, "Emotional nature and instinctual responses.")
    
    def _interpret_rising(self, sign: str) -> str:
        """Quick Rising sign interpretation"""
        interpretations = {
            "Aries": "You appear bold, direct, and energetic. First impression: pioneering and confident.",
            "Taurus": "You appear calm, reliable, and grounded. First impression: stable and pleasant.",
            "Gemini": "You appear curious, witty, and versatile. First impression: quick and engaging.",
            "Cancer": "You appear gentle, protective, and empathetic. First impression: caring and sensitive.",
            "Leo": "You appear confident, warm, and charismatic. First impression: radiant and generous.",
            "Virgo": "You appear modest, helpful, and analytical. First impression: precise and thoughtful.",
            "Libra": "You appear charming, diplomatic, and graceful. First impression: balanced and pleasant.",
            "Scorpio": "You appear intense, magnetic, and private. First impression: powerful and mysterious.",
            "Sagittarius": "You appear optimistic, adventurous, and open. First impression: friendly and philosophical.",
            "Capricorn": "You appear serious, professional, and reserved. First impression: responsible and mature.",
            "Aquarius": "You appear unique, friendly, and progressive. First impression: unconventional and interesting.",
            "Pisces": "You appear gentle, dreamy, and compassionate. First impression: ethereal and artistic."
        }
        return interpretations.get(sign, "Your outward persona and approach to life.")


def get_timezone_suggestions(country: str = None) -> List[str]:
    """
    Get common timezone suggestions
    
    This is a simplified version - in production, you'd use a timezone library
    """
    common_timezones = [
        "UTC",
        "America/New_York",
        "America/Chicago",
        "America/Los_Angeles",
        "Europe/London",
        "Europe/Paris",
        "Europe/Berlin",
        "Asia/Tokyo",
        "Asia/Shanghai",
        "Australia/Sydney",
        "America/Toronto",
        "America/Mexico_City",
        "Asia/Dubai",
        "Asia/Kolkata",
        "Pacific/Auckland"
    ]
    
    return common_timezones