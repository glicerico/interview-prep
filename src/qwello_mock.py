"""
Mock implementation of the Qwello API client for testing purposes.
This module provides simulated responses without requiring actual API access.
"""

import json
import random
from typing import Dict, Any, Optional


class MockQwelloAPI:
    """
    A mock implementation of the Qwello API client for testing.
    Simulates API responses based on guest name and focus areas.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the mock Qwello API.
        
        Args:
            api_key: Optional API key (not used but included for compatibility)
        """
        self.api_key = api_key or "mock_api_key"
        # Dictionary of pre-defined guest profiles
        self._guest_data = {
            "bernie sanders": self._create_bernie_sanders_data(),
            "jane goodall": self._create_jane_goodall_data(),
            "rosa luxemburg": self._create_rosa_luxemburg_data(),
        }
        
    def query(self, guest_name: str, focus_areas: str) -> Dict[str, Any]:
        """
        Simulate a query to the Qwello API.
        
        Args:
            guest_name: Name of the guest
            focus_areas: Comma-separated list of focus areas
            
        Returns:
            Dict containing simulated response data
        """
        # Normalize guest name for lookup
        guest_name_normalized = guest_name.lower()
        
        # Check if we have pre-defined data for this guest
        if guest_name_normalized in self._guest_data:
            response_data = self._guest_data[guest_name_normalized]
        else:
            # Generate generic data for unknown guests
            response_data = self._create_generic_guest_data(guest_name, focus_areas)
        
        # Customize response based on provided focus areas
        response_data = self._customize_for_focus_areas(response_data, focus_areas)
        
        return response_data
    
    def _customize_for_focus_areas(self, data: Dict[str, Any], focus_areas: str) -> Dict[str, Any]:
        """Customize the response data based on specified focus areas."""
        areas_list = [area.strip() for area in focus_areas.split(',')]
        
        # Add a paragraph about each focus area if not already covered
        additional_content = "\n\nIn addition, the guest has expressed interest in discussing: "
        for area in areas_list:
            additional_content += f"\n- {area}: The guest has notable insights on {area} " \
                                 f"and has been involved in several projects related to this field."
        
        data["text"] += additional_content
        return data
        
    def _create_generic_guest_data(self, guest_name: str, focus_areas: str) -> Dict[str, Any]:
        """Create generic guest data for unknown guests."""
        areas = [area.strip() for area in focus_areas.split(',')]
        
        achievements = [
            f"Published work on {random.choice(areas)}",
            f"Recognized expert in {random.choice(areas)}",
            f"Frequent speaker on topics related to {random.choice(areas)}",
            f"Contributed to several publications about {random.choice(areas)}"
        ]
        
        background = [
            f"Holds a degree in a field related to {random.choice(areas)}",
            f"Has over {random.randint(5, 25)} years of experience",
            f"Started career at a well-known organization in the field",
            f"Currently focused on advancing knowledge in {random.choice(areas)}"
        ]
        
        text = f"""
{guest_name} is a professional known for their work in {', '.join(areas)}. 

Background:
{random.choice(background)}
{random.choice(background)}

Notable Achievements:
- {random.choice(achievements)}
- {random.choice(achievements)}
- {random.choice(achievements)}

Recent Work:
{guest_name} has been exploring the intersection of {' and '.join(areas[:2] if len(areas) > 1 else areas)}
and has developed unique perspectives on these topics. Their approach combines theoretical
understanding with practical applications, making their insights valuable for both
academic and industry audiences.

Interview Considerations:
The guest is known to be {random.choice(['passionate', 'thoughtful', 'analytical', 'visionary'])}
about their work and responds well to {random.choice(['detailed technical questions', 'big-picture discussions', 'questions about real-world impact', 'exploring future possibilities'])}.
"""
        return {"text": text}

    def _create_bernie_sanders_data(self) -> Dict[str, Any]:
        """Create pre-defined data for Bernie Sanders."""
        return {
            "text": """
Bernie Sanders is an American politician who has served as the junior United States senator from Vermont since 2007. Born in Brooklyn, New York in 1941, Sanders is the longest-serving independent in U.S. congressional history, though he caucuses with the Democratic Party.

Political Background:
Sanders began his political career as the mayor of Burlington, Vermont from 1981 to 1989. He served as Vermont's sole congressman in the House of Representatives from 1991 to 2007 before being elected to the Senate. He has run for the Democratic Party's presidential nomination twice, in 2016 and 2020, gaining significant support and influencing the party's platform.

Notable Policy Positions:
- Advocate for Medicare for All, a single-payer healthcare system
- Proponent of free public college tuition and student debt forgiveness
- Champion of a $15 minimum wage (which has since become mainstream)
- Critic of income and wealth inequality
- Supporter of the Green New Deal to address climate change
- Advocate for expanded Social Security benefits
- Critic of corporate influence in politics and supporter of campaign finance reform

Legislative Achievements:
Despite being an independent, Sanders has worked within the system to pass legislation, often through amendments. He has been called the "amendment king" for his ability to add progressive provisions to larger bills. As chair of the Senate Veterans' Affairs Committee, he co-authored a major veterans' healthcare reform bill in 2014. More recently, as chair of the Senate Budget Committee, he has played a significant role in budget reconciliation processes.

Communication Style:
Sanders is known for his direct, passionate speaking style and Brooklyn accent. He tends to focus consistently on economic issues and class disparities regardless of the specific topic at hand. He often uses statistics to illustrate wealth and income inequality. His messaging has remained remarkably consistent throughout his political career.

Personal Background:
Sanders is the son of Jewish immigrants from Poland. He attended Brooklyn College and later the University of Chicago, where he was involved in civil rights activism. Before his political career, he worked various jobs including carpenter, filmmaker, and writer. His modest personal wealth compared to many other senators has been consistent with his political message about economic inequality.

Current Focus:
In recent years, Sanders has continued to advocate for progressive policies while working within the Democratic caucus. He has focused on building a movement beyond his own campaigns, supporting progressive candidates across the country. He continues to emphasize economic justice, healthcare reform, and addressing climate change as his core issues.
"""
        }

    def _create_jane_goodall_data(self) -> Dict[str, Any]:
        """Create pre-defined data for Jane Goodall."""
        return {
            "text": """
Dr. Jane Goodall is a world-renowned ethologist, conservationist, and UN Messenger of Peace. Born in London in 1934, she has dedicated her life to the study of chimpanzees and to wildlife conservation efforts globally.

Professional Background:
Dr. Goodall began her landmark study of chimpanzee behavior in Tanzania in 1960, under the mentorship of anthropologist and paleontologist Dr. Louis Leakey. Her work at Gombe Stream National Park revolutionized our understanding of chimpanzees and challenged conventional scientific perspectives about the relationship between humans and animals.

Notable Achievements:
- Discovered that chimpanzees make and use tools, a finding that forced science to reconsider the definition of humanity
- Founded the Jane Goodall Institute in 1977, which continues her research and focuses on conservation
- Established Roots & Shoots, a global environmental and humanitarian youth program
- Author of numerous books including "In the Shadow of Man" and "Reason for Hope"
- Recipient of countless awards including the UNESCO Gold Medal Award, the Kyoto Prize, and the Benjamin Franklin Medal in Life Science

Current Focuses:
At over 85 years of age, Dr. Goodall continues to travel the world advocating for environmental conservation, animal welfare, and humanitarian causes. She focuses particularly on connecting conservation with the needs of local communities and sustainable development. She has become increasingly vocal about climate change and its effects on wildlife habitats.

Interview Style:
Dr. Goodall is known for her gentle, thoughtful communication style and her ability to inspire through personal stories. She often speaks about hope in the face of environmental challenges and emphasizes individual action. She frequently incorporates anecdotes about specific chimpanzees she has known to illustrate her points about animal intelligence and emotion.

Philosophy:
Her philosophy centers around the interconnectedness of all living things and the responsibility of humans to protect the natural world. She emphasizes the importance of making daily choices that reduce our environmental impact and the power of young people to effect positive change.

Recent Work:
Dr. Goodall has adapted to the digital age, continuing her advocacy work through virtual lectures, podcasts, and social media during periods when travel has been limited. She has spoken increasingly about the connections between environmental destruction, wildlife trafficking, and global health crises.
"""
        }

    def _create_rosa_luxemburg_data(self) -> Dict[str, Any]:
        """Create pre-defined data for Rosa Luxemburg."""
        return {
            "text": """
Rosa Luxemburg was a Polish Marxist theorist, philosopher, economist, anti-war activist, and revolutionary socialist. Born in Poland (then part of the Russian Empire) in 1871, she became a naturalized German citizen and was one of the most influential figures in European socialist thought in the late 19th and early 20th centuries.

Historical Background:
Luxemburg was a key figure in the socialist movement in Germany and Poland. She co-founded the Communist Party of Germany (KPD) and was a leading member of the Social Democratic Party of Germany (SPD) before breaking with them over their support for World War I. She was murdered in January 1919 during the German Revolution, becoming a martyr for the socialist cause.

Theoretical Contributions:
- Developed a critique of capitalism that emphasized its inherent tendency toward imperialism and militarism
- Advanced the theory of "spontaneity," arguing that revolutionary consciousness emerges from workers' struggles rather than being imposed by a vanguard party
- Advocated for democratic socialism, criticizing both reformist social democracy and authoritarian communism
- Wrote extensively on political economy, imperialism, nationalism, and revolutionary strategy
- Key works include "The Accumulation of Capital," "Reform or Revolution," and "The Mass Strike"

Political Positions:
Luxemburg was a committed internationalist who opposed nationalism and militarism. She criticized both the reformism of the SPD and later the authoritarianism of the Bolsheviks under Lenin. She believed in the necessity of revolution but insisted it must be democratic in both means and ends. Her famous quote, "Freedom is always the freedom of dissenters," reflected her commitment to democratic principles within revolutionary movements.

Legacy:
Luxemburg's ideas have influenced generations of socialists, feminists, and anti-war activists. Her emphasis on democracy within socialism has been particularly important for democratic socialist and council communist traditions. Her critique of capitalism's relationship to imperialism remains relevant to contemporary anti-globalization movements. Her writings on the mass strike and spontaneous action have influenced theories of social movements.

Personal Life:
Luxemburg faced multiple forms of discrimination as a Jewish woman with a disability (she had a slight limp from a childhood illness). She was a gifted writer and orator who maintained passionate intellectual and personal relationships. Her letters, especially those written from prison, reveal a person deeply engaged with literature, nature, and human relationships alongside her political commitments.

Historical Context:
Luxemburg lived during a period of intense social and political upheaval in Europe. The rise of mass socialist parties, the outbreak of World War I, and the Russian Revolution all shaped her thinking and activism. Her murder by right-wing paramilitaries (Freikorps) came during the tumultuous aftermath of Germany's defeat in World War I, as revolutionary and counter-revolutionary forces battled for control.
"""
        }


    def make_request(self, url: str, payload: Dict[str, str], headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Simulate making an HTTP request to the Qwello API.
        
        Args:
            url: The API endpoint
            payload: Request parameters
            headers: HTTP headers including authentication
            
        Returns:
            Dict containing the simulated response data
        """
        # Extract the guest name and focus areas from the payload
        guest_name = payload.get("guest_name", "Unknown Guest")
        focus_areas = payload.get("focus_areas", "general")
        
        # Get the simulated response data
        response_data = self.query(guest_name, focus_areas)
        
        # Simulate an HTTP response structure
        return {
            "status_code": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "json": response_data,
            "text": json.dumps(response_data)
        } 