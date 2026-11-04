from dataclasses import dataclass, field,asdict
from itertools import product, combinations
import json
from pathlib import Path
from typing import ClassVar
import sys
import atexit
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.formatting.rule import ColorScaleRule
from openpyxl.utils import get_column_letter

class Tee:
    """Writes console output to both the console and a log file."""

    def __init__(self, *streams):
        self.streams = streams

    def write(self, text):
        for stream in self.streams:
            stream.write(text)
            stream.flush()

    def flush(self):
        for stream in self.streams:
            stream.flush()
# artifact_data.py
VESNA_MAIN_STATS = {
    "flower": {"stat": "HP", "value": 4780},
    "feather": {"stat": "ATK", "value": 311},
    "sands": {"stat": "ATK%", "value": 46.60},
    "goblet": {"stat": "ATK%", "value": 46.60},
    "circlet": {"stat": "CD%", "value": 62.20},
}
ARTIFACT_SUBSTATS = {
    "HP": {
        "max_3line": 20,
        "max_4line": 24,
        "rolls": [209.13, 239.00, 268.88, 298.75],
        "average": 253.94,
        "unit": "flat",
    },
    "HP%": {
        "max_3line": 25,
        "max_4line": 30,
        "rolls": [4.08, 4.66, 5.25, 5.83],
        "average": 4.955,
        "unit": "percent",
    },
    "ER%": {
        "max_3line": 25,
        "max_4line": 30,
        "rolls": [4.53, 5.18, 5.83, 6.48],
        "average": 5.505,
        "unit": "percent",
    },
    "DEF": {
        "max_3line": 25,
        "max_4line": 30,
        "rolls": [16.20, 18.52, 20.83, 23.15],
        "average": 19.675,
        "unit": "flat",
    },
    "DEF%": {
        "max_3line": 25,
        "max_4line": 30,
        "rolls": [5.10, 5.83, 6.56, 7.29],
        "average": 6.195,
        "unit": "percent",
    },
    "ATK": {
        "max_3line": 20,
        "max_4line": 24,
        "rolls": [13.62, 15.56, 17.51, 19.45],
        "average": 16.535,
        "unit": "flat",
    },
    "ATK%": {
        "max_3line": 15,
        "max_4line": 18,
        "rolls": [4.08, 4.66, 5.25, 5.83],
        "average": 4.955,
        "unit": "percent",
    },
    "CR%": {
        "max_3line": 25,
        "max_4line": 30,
        "rolls": [2.72, 3.11, 3.50, 3.89],
        "average": 3.305,
        "unit": "percent",
    },
    "CD%": {
        "max_3line": 20,
        "max_4line": 24,
        "rolls": [5.44, 6.22, 6.99, 7.77],
        "average": 6.605,
        "unit": "percent",
    },
    "EM": {
        "max_3line": 25,
        "max_4line": 30,
        "rolls": [16.32, 18.65, 20.98, 23.31],
        "average": 19.815, 
        "unit": "flat",
    },
}
ARTIFACT_RULES = {
    "3_line": {
        "total_substat_rolls": 40,
        "max_rolls_per_stat_per_artifact": 5,
    },
    "4_line": {
        "total_substat_rolls": 45,
        "max_rolls_per_stat_per_artifact": 6,
    },
}
DISTRIBUTION_CONFIG = {
    "3_line": {
        "total_rolls": 40,
        "reserved_rolls": {
            "CR%": 11,
            "ER%": 2,
        },
    },
    "4_line": {
        "total_rolls": 45,
        "reserved_rolls": {
            "CR%": 11,
            "ER%": 2,
        },
    },
}
def build_artifact_map(line_type):
    """Generates the allowed substats for each artifact."""

    if line_type not in ARTIFACT_RULES:
        raise ValueError(f"Unknown Artifact Type: {line_type}")

    max_per_artifact = ARTIFACT_RULES[line_type][
        "max_rolls_per_stat_per_artifact"
    ]

    suffix = "3line" if line_type == "3_line" else "4line"

    artifact_map = {}

    for slot, artifact in VESNA_MAIN_STATS.items():
        main_stat = artifact["stat"]
        
        artifact_map[slot] = {
            "main_stat": main_stat,
            "main_value": artifact["value"],
            "substats": {
                stat: {
                    "max_rolls_total": data[f"max_{suffix}"],
                    "max_rolls_per_artifact": max_per_artifact,
                    "average": data["average"],
                    "roll_values": data["rolls"],
                    "unit": data["unit"],
                }
                for stat, data in ARTIFACT_SUBSTATS.items()
                if stat != main_stat
            },
        }

    return artifact_map
ARTIFACT_MAP_3_LINE = build_artifact_map("3_line")
ARTIFACT_MAP_4_LINE = build_artifact_map("4_line")
# 2. VESNA OBJECT
VESNA_ROTATION = [
    {"name": "E", "mv": 0.72, "type": "stellar"},
    {"name": "sE1", "mv": 0.72, "type": "stellar"},
    {"name": "sE2", "mv": 1.80, "type": "stellar"},
    {"name": "Q_spirit", "mv": 4.7376, "type": "stellar"},
    {"name": "sE3_spirit_1", "mv": 0.8064, "type": "stellar"},
    {"name": "sE3_spirit_2", "mv": 0.8064, "type": "stellar"},
    {"name": "sE3_spirit_3", "mv": 0.8064, "type": "stellar"},
    {"name": "sE3_spirit_4", "mv": 0.8064, "type": "stellar"},
    {"name": "sE3_final", "mv": 2.8224, "type": "stellar"},
]

@dataclass
class VesnaTeamDPSTheory:
   # Vesna is always using her Signature and Scarlet Proof Set
   # 1. GENERAL COMBAT AND ENEMY STATS
    general_defense_multiplier_90: float = 190 / 390
    general_defense_multiplier_95: float = 195 / 395
    general_defense_multiplier_100: float = 0.5

    enemy_anemo_resistance: float = 10
    enemy_cryo_resistance: float = 10

    lv90_modifier: float = 1446
    lv95_modifier: float = 1562
    vortex_lv_100_modifier: float = 1675

    vortex_procs: float = 16
    vortex_explosions: float = 5.5
    vortex_procs_vodyanitsa: float = 12
    vortex_explosions_vodyanitsa: float = 3
    #Fuction to determine which character is holding which artifact set and its buffs
    @property
    def active_team_artifact_set_distribution_and_buffs(self) -> dict:
        """Dynamically assigns artifact sets and returns their effects and conditions."""

        buffs = {}
        # --------------------------------------------------
        # 1. Determine artifact set holders
        # --------------------------------------------------

        # Furnace priority: Odette > Faruzan > Lumine > Sucrose
        if self.is_odette_active:
            furnace_holder = "odette"
        elif self.is_faruzan_active:
            furnace_holder = "faruzan"
        elif self.is_lumine_active:
            furnace_holder = "lumine"
        else:
            furnace_holder = "sucrose"

        # ToM holder: Vodyanitsa > Diona > Lumine
        if self.is_vodyanitsa_active:
            tom_holder = "vodyanitsa"
        elif self.is_diona_active:
            tom_holder = "diona"
        elif self.is_lumine_active:
            tom_holder = "lumine"
        else:
            tom_holder = None

        # Noblesse holder
        if self.is_vodyanitsa_active and self.is_diona_active:
            noblesse_holder = "diona"
        elif self.is_diona_active and self.is_lumine_active:
            noblesse_holder = "diona"
        elif (
            self.is_vodyanitsa_active
            and self.is_lumine_active
            and tom_holder != "lumine"
            and furnace_holder != "lumine"
        ):
            noblesse_holder = "lumine"
        else:
            noblesse_holder = None

        # Tsaritsa-Set holder
        tsaritsa_holder = "anastasya" if self.is_anastasya_active else None

        # Lumine 2pc/2pc ATK: only if Lumine does not already hold Noblesse
        atk_2p2p_holder = (
            "lumine"
            if self.is_vodyanitsa_active
            and self.is_lumine_active
            and not self.is_diona_active
            and noblesse_holder != "lumine"
            else None
        )

        # --------------------------------------------------
        # 2. Furnace set
        # --------------------------------------------------

        buffs["furnace"] = {
            "holder": furnace_holder,
            "holder_atk_bonus": 30.0,
            "stellar_damage_bonus": self.odette_furnace_set_stellar_damage_bonus,
            "uptime": {
                "vesna": 1.0 if furnace_holder != "lumine" else 1.0,
                "others": 1.0 if furnace_holder in ("odette", "faruzan", "sucrose") else 0.0,
            },
            "conditions": {
                # When Lumine holds Furnace, the team bonus applies to Vesna
                # at 100% uptime, but only to other characters' off-field Stellar damage.
                "lumine_holder_other_characters_off_field_only": True,
            },
        }

        # --------------------------------------------------
        # 3. Noblesse Oblige
        # --------------------------------------------------

        buffs["noblesse"] = {
            "holder": noblesse_holder,
            "atk_bonus": 20.0,
            "duration": 12.0,
            "uptime": {
                # Vesna's damage always benefits from Noblesse.
                "vesna": 1.0,
                # For other characters, the buff only counts for off-field damage.
                "others": 0.0,
            },
            "conditions": {
                "others_off_field_only": True,
            },
        }

        # --------------------------------------------------
        # 4. Tenacity of the Millelith (ToM)
        # --------------------------------------------------

        buffs["tom"] = {
            "holder": tom_holder,
            "atk_bonus": 20.0,
            "uptime": 1.0 if tom_holder is not None else 0.0,
            "conditions": {
                # ToM benefits every character and every damage type.
                "all_characters": True,
                "all_damage_types": True,
            },
        }

        # --------------------------------------------------
        # 5. Viridescent Venerer (VV)
        # --------------------------------------------------

        buffs["vv"] = {
            "holder": "faruzan" if self.is_faruzan_active and furnace_holder != "faruzan" else None,
            "cryo_res_reduction": 40.0,
        }

        # --------------------------------------------------
        # 6. Lumine's 2-piece + 2-piece ATK sets
        # --------------------------------------------------

        buffs["atk_2p2p"] = {
            "holder": atk_2p2p_holder,
            "atk_bonus": 36.0,
        }

        # --------------------------------------------------
        # 7. Instructor
        # --------------------------------------------------

        instructor_holder = (
            "sucrose"
            if self.is_sucrose_active and furnace_holder != "sucrose"
            else None
        )

        buffs["instructor"] = {
            "holder": instructor_holder,
            "uptime": 0.8 if self.is_odette_active and instructor_holder is not None else 0.0,
            "rotation_duration": 20.0 if self.is_odette_active and instructor_holder is not None else None,
            "conditions": {
                # The rotation switches to Sucrose twice before Odette and Vesna.
                "odette_and_vesna_uptime_80_percent": instructor_holder is not None,
            },
        }
        # --------------------------------------------------
        # 8. Tsaritsa set
        # --------------------------------------------------
        buffs["tsaritsa"] = {
            "holder": tsaritsa_holder,
            "atk_bonus": 18.0,
            "crit_rate_bonus": 20.0,
            "stellar_crit_rate_bonus": 40.0,
            "uptime": 1.0 if self.is_anastasya_active else 0.0,
            "conditions": {
                "all_characters": False,
                "all_damage_types": False,
            },
        }
        return buffs
    #Team Rotation length
    @property
    def rotation_duration(self) -> float:
        return 22.5 if self.is_anastasya_active else 19.5
    # Common flat atk bonus from party
    @property
    def team_flat_atk_common_bonus(self) -> float:
        return (
            self.vodyanitsa_C1_flat_atk_bonus
            if self.is_vodyanitsa_active and self.vodyanitsa_constellation >= 1
            else 0.0
        )
    #Team wide ATK% form talents, weapons, cons or artifact sets
    def team_atk_percent_common_bonus(self, character: str) -> float:
        buff = 0.0

        # Tenacity of the Millelith
        if self.active_team_artifact_set_distribution_and_buffs["tom"]["holder"] is not None:
            buff += 20.0

        # Odette: Marvelous Splendor C2
        if self.is_odette_active and self.odette_constellation >= 2:
            if character != "odette":
                buff += (self.odette_C2_marvelous_splender_stacks_atk_percent * self.odette_marvelous_splender_stacks)

        return buff / 100.0

    # Team-wide ATK% bonus from variable buffs
    def team_atk_percent_variable_bonus(self, character: str, on_field: bool) -> float:
        buff = 0.0

        # Noblesse Oblige
        if self.active_team_artifact_set_distribution_and_buffs["noblesse"]["holder"] is not None:
            if character == "vesna":
                buff += 20.0
            elif not on_field:
                buff += 20.0 * (12.0 / self.rotation_duration)
        # Vodyanitsa: Signature Weapon
        if self.is_vodyanitsa_active and on_field:
            buff += self.vodyanitsa_signature_atk_bonus

        # Anastasya: C1 ATK bonus for Cryo characters
        if self.is_anastasya_active and self.anastasya_constellation >= 1:
            if character in ("odette", "lumine", "diona"):
                buff += self.anastasya_C1_cryo_character_atk_buff

        return buff / 100.0

    #General Teamwide EM buffs applied to specific Characters
    def team_em_buff(self, character: str) -> float:
        buff = 0.0

        # Diona C6 EM buff only applies to Vesna
        if self.is_diona_active and character == "vesna":
            buff += self.diona_C6_EM_value

        # Vesna receives an additional A3 EM bonus when Vodya is in the team
        if self.is_vodyanitsa_active and character == "vesna":
            buff += self.em_bonus_vesna_a3_talent_other_solo

        if self.is_sucrose_active:

            # Apply full Sucrose buffs when Lumine is in the team
            if self.is_lumine_active and character in ("lumine", "odette", "vesna"):
                buff += self.sucrose_instrcutor_team_buff_em_value
                buff += self.sucrose_talent_catalyst_conversion_bonus_em_value
                buff += self.sucrose_talent_mollis_favonius_em_value

            # Apply Odette buffs when Lumine is not in the team
            elif character == "odette":
                buff += self.sucrose_instrcutor_team_buff_em_value
                buff += self.sucrose_talent_catalyst_conversion_bonus_em_value
                buff += self.sucrose_talent_mollis_favonius_em_value

            # Apply reduced Sucrose buffs to Vesna without Lumine
            elif character == "vesna":
                vesna_sucrose_buff = (
                    self.sucrose_instrcutor_team_buff_em_value
                    + self.sucrose_talent_mollis_favonius_em_value
                )

                buff += vesna_sucrose_buff * 0.75
        # Anastasya C1 EM buff for non-Cryo characters
        if self.is_anastasya_active and self.anastasya_constellation >= 1:
            if character not in ("odette", "lumine", "diona", "anastasya"):
                buff += 60.0

        return buff

    #Team wide Stellar Bonuses from talents, weapons, cons or artifact sets
    @property
    def team_stellar_damage_bonus(self) -> float:
        """Team-wide Stellar damage bonuses."""

        buff = 0.0

        # Furnace set bonus
        if self.active_team_artifact_set_distribution_and_buffs["furnace"]["holder"] is not None:
            buff += self.odette_furnace_set_stellar_damage_bonus

        # Faruzan: Breezeborne R5
        if self.is_faruzan_active or self.is_diona_active or self.is_anastasya_active:
            buff += self.faruzan_breezeborne_r5_stellar_damage_bonus

        # Lumine: Stellar Jubilee
        if self.is_lumine_active:
            buff += 40.0
        if self.is_anastasya_active:
            buff += 50.0

        return buff / 100.0
    #General Stellar Anemo Crit damage
    def calculate_stellar_crit_multiplier(self, character: str, element: str) -> float:

        # 1. Charakterbezogenen Krit-Schaden bestimmen
        if character == "vesna":
            crit_damage = (
                  self.crit_damage_base
                + self.crit_damage_circlet
                + self.crit_damage_signature
                + self.crit_damage
                + self.weapon_proc_crit_damage
            )

        elif character == "odette":
            crit_damage = self.odette_cd

        elif character == "lumine":
            crit_damage = self.lumine_total_CD

        elif character == "anastasya":
            # Temporarily use Lumine's Crit-DMG profile
            crit_damage = self.lumine_total_CD 

        else:
            raise ValueError(f"Unknown character: {character}")

        # 2. Vodyanitsa C2: Stellar Crit-DMG
        if (self.is_vodyanitsa_active and self.current_configuration["constellations"].get("vodyanitsa", 0) >= 2):
            crit_damage += self.vodyanitsa_C2_stellar_reaction_cd_bonus

        # 3. Elemental Crit Damage Mods
        if element == "anemo":
            if self.is_faruzan_active:
                crit_damage += self.faruzan_c6_anemo_crit_damage

        elif element != "cryo":
            raise ValueError(f"Unsupported Stellar element: {element}")
        # 4. Anastasya: Team-wide Stellar Crit-DMG bonus
        if self.is_anastasya_active:
            crit_damage += (
                12.0 * (3.0 / self.rotation_duration)
                + 4.0 * ((self.rotation_duration - 3.0) / self.rotation_duration)
            )

        # 5. Anastasya C2: Stellar Crit-DMG
        if character == "anastasya" and self.is_anastasya_active and self.anastasya_constellation >= 2:
            crit_damage += self.anastasya_C2_stellar_CD_mod

        multiplier = 1.0 + crit_damage / 100.0

        # 6. Anastasya C2: Stellar Elevation
        if self.is_anastasya_active and self.anastasya_constellation >= 2:
            multiplier *= self.anastasya_C2_stellar_elevation_mod

        return multiplier
    # General EMM Multiplier for Vesna, Odette, Lumine, Anastasya
    def calculate_stellar_damage_multiplier(self, character: str, on_field: bool = True) -> float:

        # 1. Determine character-specific Elemental Mastery
        if character == "vesna":
            elemental_mastery = self.vesna_em_value
            personal_stellar_bonus = (
                self.vesna_weapon_stellar_bonus
                + self.vesna_artifact_set_stellar_bonus
            ) / 100.0

        elif character == "odette":
            elemental_mastery = self.odette_em
            personal_stellar_bonus = 30.0 / 100.0

        elif character == "lumine":
            elemental_mastery = self.lumine_base_em_value
            personal_stellar_bonus = 0.0

        elif character == "anastasya":
            elemental_mastery = self.anastasya_total_em
            personal_stellar_bonus = 0.0

        else:
            raise ValueError(f"Unknown character: {character}")

        # 2. Odette: Marvelous Splendor C1
        if self.is_odette_active:
            stacks = (
                self.odette_C1_marvelous_splender_stacks
                if self.odette_constellation >= 1
                else self.odette_marvelous_splender_stacks
            )

            # Odette receives the bonus only while on-field
            if character == "odette" and on_field:
                personal_stellar_bonus += (
                    stacks * self.odette_C0_stellar_damage / 100.0
                )

            # Other characters receive the transferred bonus
            elif character != "odette":
                personal_stellar_bonus += (
                    stacks * self.odette_C0_stellar_damage / 100.0
                )

        # 3. Calculate talent-based Stellar damage bonuses (14% Vesna, Odette, Anastasya, 7% Lumine)
        talent_stellar_bonus = (
            (self.odette_talent_stellar_damage_bonus if self.is_odette_active else 0.0)
            + self.vesna_talent_stellar_base_damage_bonus
            + (
                self.lumine_stellar_jubilee_talent_stellar_base_damage_mod
                if self.is_lumine_active else 0.0
            )
            + (
                self.anastasya_talent_stellar_base_damage_mod
                if self.is_anastasya_active else 0.0
            )
        ) / 100.0
        # 4. Calculate final Stellar damage multiplier
        return (
            (1.0 + talent_stellar_bonus)
            * (
                1.0
                + (6.0 * elemental_mastery) / (elemental_mastery + 2000.0)
                + self.team_stellar_damage_bonus
                + personal_stellar_bonus
            )
        )

    #Team wide modified cryo resistance resulting in its multiplicator
    @property
    def calculate_anemo_res_multiplier(self) -> float:
        resistance_reduction = 0.0

        if self.is_faruzan_active:
            resistance_reduction += self.faruzan_anemo_res_reduction

        if self.is_vodyanitsa_active:
            resistance_reduction += self.vodyanitsa_anemo_res_reduction

        effective_resistance = (
            self.enemy_anemo_resistance - resistance_reduction
        ) / 100.0

        if effective_resistance < 0.0:
            return 1.0 - effective_resistance / 2.0

        if effective_resistance < 0.75:
            return 1.0 - effective_resistance

        return 1.0 / (4.0 * effective_resistance + 1.0)
    #Team wide modified cryo resistance resulting in its multiplicator
    @property
    def calculate_cryo_res_multiplier(self) -> float:
        resistance_reduction = 0.0

        if self.is_vodyanitsa_active:
            resistance_reduction += self.vodyanitsa_cryo_res_reduction

        if self.is_odette_active and self.odette_constellation >= 2:
            resistance_reduction += self.odette_C2_cryo_res_reduction

        if self.active_team_artifact_set_distribution_and_buffs["vv"]["holder"] == "faruzan":
            resistance_reduction += self.faruzan_VV_set_cryo_res_reduction

        effective_resistance = (
            self.enemy_cryo_resistance - resistance_reduction
        ) / 100.0

        if effective_resistance < 0.0:
            return 1.0 - effective_resistance / 2.0

        if effective_resistance < 0.75:
            return 1.0 - effective_resistance

        return 1.0 / (4.0 * effective_resistance + 1.0)

    @property
    def vesna_constellation(self) -> int:
        return int(self.current_configuration.get("constellations", {}).get("vesna", 0))

    @property
    def odette_constellation(self) -> int:
        return int(self.current_configuration.get("constellations", {}).get("odette", 0))

    @property
    def vodyanitsa_constellation(self) -> int:
        return int(self.current_configuration.get("constellations", {}).get("vodyanitsa", 0))
    
    @property
    def anastasya_constellation(self) -> int:
        return int(self.current_configuration.get("constellations", {}).get("anastasya", 0))

    @property
    def active_team_members(self) -> list[str]:
        return self.active_team["members"]

    @property
    def is_diona_active(self) -> bool:
        return "diona" in self.active_team_members

    @property
    def is_faruzan_active(self) -> bool:
        return "faruzan" in self.active_team_members

    @property
    def is_sucrose_active(self) -> bool:
        return "sucrose" in self.active_team_members

    @property
    def is_vodyanitsa_active(self) -> bool:
        return "vodyanitsa" in self.active_team_members

    @property
    def is_odette_active(self) -> bool:
        return "odette" in self.active_team_members

    @property
    def is_lumine_active(self) -> bool:
        return "lumine" in self.active_team_members

    @property
    def is_anastasya_active(self) -> bool:
        return "anastasya" in self.active_team_members

    # 2. VESNA – character stats and MV
    vesna_level_90: int = 90
    vesna_level_95: int = 95
    level: int = 90 #change lv 90 / 95 / 100 to evaluate which level Vesna is
    base_atk_lv_90: float = 1028
    base_atk_lv_95: float = 1068
    vesna_flat_atk_feather: float = 311
    vesna_base_em: float = 0.0

    atk_percent_vesna_a3_talent_cryo_anemo_solo: float = 6
    atk_percent_vesna_a3_talent_cryo_anemo_duo: float = 12
    atk_percent_vesna_a3_talent_cryo_anemo_trio: float = 18 #caps here if vodya is in the team
    atk_percent_vesna_a3_talent_cryo_anemo_quartett: float = 24

    em_bonus_vesna_a3_talent_other_solo: float = 25 #if Vodya is in the team
    em_bonus_vesna_a3_talent_other_duo: float = 50
    em_bonus_vesna_a3_talent_other_trio: float = 75 #Vesna + 3 not cryo/anemo

    atk_percent_sands: float = 46.6
    atk_percent_goblet: float = 46.6
    atk_percent_set_bonus: float = 18
    crit_damage_circlet: float = 62.2
    vesna_artifact_set_stellar_bonus: float = 40.0

    crit_damage_base: float = 50
    crit_damage_signature: float = 44.1
    weapon_proc_crit_damage: float = 56
    vesna_weapon_stellar_bonus: float = 36.0

    flat_attack_value: float = 0.0
    atk_percent: float = 0.0
    crit_rate: float = 1.0
    crit_damage: float = 0.0
    elemental_mastery: float = 0.0
    energy_recharge: float = 0.0

    anemo_mv: float = 1521.32
    stellar_anemo_mv: float = 3633.00

    vesna_talent_stellar_base_damage_bonus: float = 14

    e_stellar_mv: float = 72
    se1_stellar_mv: float = 72
    se2_stellar_mv: float = 180

    se1_stage_damage_multiplier: float = 1.1
    se2_stage_damage_multiplier: float = 1.2
    stellar_Q_damage_multiplier: float = 1.4

    se3_stage1_multiplier: float = 1.4
    se3_stage2_multiplier: float = 1.5
    se3_stage3_multiplier: float = 1.6

    se3_spirit_mv: float = 80.64
    se3_final_mv: float = 282.24
    se3_spirit_hits: int = 4
    stellar_Q_damage_MV: float = 473.76

    vesna_C1_additional_stellar_mv: float = 604.80
    se_stage_0_multiplier: float = 1.6
    vesna_C2_atk_value: float = 40


    # 3. ODETTE STATS
    # We are simulating Odette in all of her teams on Furnace set
    # Character stats
    odette_lv: float = 90.0
    odette_atk: float = 2713.0 #idle atk value
    odette_base_atk: float = 877.0
    odette_em: float = 103.0
    odette_cr: float = 88.8
    odette_cd: float = 220.5

    odette_furnace_set_stellar_damage_bonus: float = 50.0


    # E-Skill – cryo damage
    odette_E_initial_mv: float = 194.54
    odette_Coda_DoT_mv: float = 172.51

    # Solo Dance Double
    odette_plume_mv: float = 77.47
    odette_wing_mv: float = 92.64
    odette_plume_hits: int = 5
    odette_wing_hits: int = 5


    # E Skill – Stellar damage components
    # Coda finisher hi
    odette_Coda_stellar_swirl_mv: float = 825.55

    # Solo Dance Double – additional Stellar hits.
    odette_plume_stellar_swirl_mv: float = 72.95

    odette_wing_stellar_swirl_mv: float = 87.24

    odette_plume_stellar_hits: int = 5
    odette_wing_stellar_hits: int = 5

    # Stellar-Damage Mods
    odette_C0_stellar_damage: float = 15.0
    odette_personal_stellar_damage_bonus: float = 30.0
    odette_talent_stellar_damage_bonus: float = 14.0

    # Marvelous Splendor – Stacks
    odette_marvelous_splender_stacks: float = 4.0

    # Constellations
    # C1
    odette_E_additional_mv: float = 450.0
    odette_C1_marvelous_splender_stacks: float = 6.0

    # C2
    odette_C2_marvelous_splender_stacks_atk_percent: float = 7.0
    odette_C2_cryo_res_reduction: float = 20.0
    odette_C2_electro_res_reduction: float = 20.0
    odette_C2_anemo_res_reduction: float = 20.0

    @property
    def odette_atk_percent_value(self) -> float:
        return self.team_atk_percent_common_bonus("vesna") + self.team_atk_percent_variable_bonus("vesna", True)
    @property
    def odette_on_field_atk(self) -> float:
        vodyanitsa_c1_bonus = (
            self.vodyanitsa_C1_flat_atk_bonus
            if (
                self.is_vodyanitsa_active
                and self.vodyanitsa_constellation >= 1
            )
            else 0.0
        )

        return (
            self.odette_atk
            + self.odette_base_atk * self.odette_atk_percent_value
            + vodyanitsa_c1_bonus
        )
    @property
    def odette_off_field_atk_percent_value(self) -> float:
        buff = 0.0

        # Tenacity of the Millelith
        if self.active_team_artifact_set_distribution_and_buffs["tom"]["holder"] is not None:
            buff += 20.0

        # Noblesse Oblige
        if self.active_team_artifact_set_distribution_and_buffs["noblesse"]["holder"] is not None:
            buff += 20.0

        return buff / 100.0
    @property
    def odette_off_field_atk(self) -> float:
        vodyanitsa_c1_bonus = (
            self.vodyanitsa_C1_flat_atk_bonus
            if (
                self.is_vodyanitsa_active
                and self.vodyanitsa_constellation >= 1
            )
            else 0.0
        )

        return (
            self.odette_atk
            + self.odette_base_atk * self.odette_off_field_atk_percent_value
            + vodyanitsa_c1_bonus
        )
    @property
    def odette_effective_cr(self) -> float:
        cr = self.odette_cr

        # Apply team CR bonus
        if self.is_lumine_active or self.is_diona_active or self.is_anastasya_active:
            cr += 15.0

        return min(cr, 100.0)
    @property
    def odette_crit_multiplier(self) -> float:
        return 1.0 + (self.odette_effective_cr / 100.0) * (self.odette_cd / 100.0)


    # 3.1 Odette Damage Calcs
    def calculate_odette_stellar_damage(self,mv: float,atk: float,on_field: bool = True,) -> float:
        damage = (atk* (mv / 100.0)* self.calculate_stellar_damage_multiplier("odette",on_field=on_field))

        # Add Vodyanitsa Stellar Quills flat damage
        damage += self.active_vodyanitsa_stellar_quills_flat_damage

        return (damage* self.odette_crit_multiplier* self.calculate_cryo_res_multiplier)

    # Odette - On-Field Cryo Damage
    @property
    def odette_on_field_cryo_damage(self) -> float:

        initial_damage = (
            self.odette_on_field_atk
            * (self.odette_E_initial_mv / 100.0)
            * 1.0
            * self.general_defense_multiplier_90
            * self.calculate_cryo_res_multiplier
            * self.odette_crit_multiplier
        )

        coda_dot_damage = (
            self.odette_on_field_atk
            * (self.odette_Coda_DoT_mv / 100.0)
            * 1.0
            * self.general_defense_multiplier_90
            * self.calculate_cryo_res_multiplier
            * self.odette_crit_multiplier
        )
        return initial_damage + 3.0 * coda_dot_damage
    #Coda Finisher Hit
    @property
    def odette_on_field_Coda_stellar_swirl_damage(self) -> float:
        return self.calculate_odette_stellar_damage(
            mv=self.odette_Coda_stellar_swirl_mv,
            atk=self.odette_on_field_atk,
            on_field=True,
        )
    # C1 Additional Stellar Hit
    @property
    def odette_on_field_C1_additional_stellar_damage(self) -> float:
        if self.odette_constellation < 1.0:
            return 0.0

        return self.calculate_odette_stellar_damage(
            mv=self.odette_E_additional_mv,
            atk=self.odette_on_field_atk,
            on_field=True,
        )
    #Stellar Plume Hits
    @property
    def odette_on_field_plume_stellar_swirl_damage(self) -> float:
        return self.calculate_odette_stellar_damage(
            mv=self.odette_plume_stellar_swirl_mv,
            atk=self.odette_on_field_atk,
            on_field=True,
        )

    #Stellar Wing Hits
    @property
    def odette_on_field_wing_stellar_swirl_damage(self) -> float:
        return self.calculate_odette_stellar_damage(
            mv=self.odette_wing_stellar_swirl_mv,
            atk=self.odette_on_field_atk,
            on_field=True,
        )

    # Stellar Hits
    @property
    def odette_off_field_Coda_stellar_swirl_damage(self) -> float:
        return self.calculate_odette_stellar_damage(
            mv=self.odette_Coda_stellar_swirl_mv,
            atk=self.odette_off_field_atk,
            on_field=False,
        )

    @property
    def odette_off_field_plume_stellar_swirl_damage(self) -> float:
        return self.calculate_odette_stellar_damage(
            mv=self.odette_plume_stellar_swirl_mv,
            atk=self.odette_off_field_atk,
            on_field=False,
        )

    @property
    def odette_off_field_wing_stellar_swirl_damage(self) -> float:
        return self.calculate_odette_stellar_damage(
            mv=self.odette_wing_stellar_swirl_mv,
            atk=self.odette_off_field_atk,
            on_field=False,
        )
    def calculate_odette_vortex_proc_damage(self, level: int) -> float:
        if level == 90:
            level_modifier = self.lv90_modifier
        elif level == 95:
            level_modifier = self.lv95_modifier
        else:
            raise ValueError(f"Unsupported enemy level: {level}")

        damage = (
            level_modifier
            * 0.75
            * 0.3
            * self.calculate_stellar_damage_multiplier("odette")
        )

        # Add Vodyanitsa Stellar Quills flat damage
        damage += self.active_vodyanitsa_stellar_quills_flat_damage

        return (
            damage
            * self.calculate_stellar_crit_multiplier("odette", "cryo")
            * self.calculate_cryo_res_multiplier
        )


    def calculate_odette_vortex_explosion_damage(self, level: int) -> float:
        if level == 90:
            level_modifier = self.lv90_modifier
        elif level == 95:
            level_modifier = self.lv95_modifier
        else:
            raise ValueError(f"Unsupported enemy level: {level}")

        damage = (
            level_modifier
            * 3.0
            * 0.3
            * self.calculate_stellar_damage_multiplier("odette")
        )

        # Add Vodyanitsa Stellar Quills flat damage
        damage += self.active_vodyanitsa_stellar_quills_flat_damage

        return (
            damage
            * self.calculate_stellar_crit_multiplier("odette", "cryo")
            * self.calculate_anemo_res_multiplier
        )


    # 4. VODYANITSA – CHARACTER STATS
    # we are running on Vodyanitsa always her Signature weapon and 2p/2p HP to reach the 65k HP threshhold
    # not running ToM will result in slightly lower numbers, but there is less headache about calculating uptimes for different artifact set combinations in different teams
    # this whole stuff might be added in the future
    vodyanitsa_HP_value: float = 65000.0
    vodyanitsa_stellar_quills_active: float = 6500.0
    vodyanitsa_flat_dps: float = 750.0
    em_vesna_talent_a3_vodyanitsa: float = 25

    vodyanitsa_anemo_res_reduction: float = 35.0
    vodyanitsa_cryo_res_reduction: float = 30.0
    vodyanitsa_signature_atk_bonus: float = 42.0
    vodyanitsa_C1_flat_atk_bonus: float = 520.0
    vodyanitsa_C2_stellar_reaction_cd_bonus: float = 60.0

    @property
    def active_vodyanitsa_stellar_quills_flat_damage(self) -> float:
        if self.is_vodyanitsa_active:
            return self.vodyanitsa_stellar_quills_active
        return 0.0

    # 5. DIONA – C6
    # Diona is C6 and uses in any case ToM Set
    # we give her ToM, even though Vodanitsa can run it aswell, for more convenient reasons. So we dont need to calc precisely uptimes on Noblesse
    atk_percent_vesna_a3_value_diona: float = 6
    diona_dps_value: float = 5000.0
    diona_tom_set_atk_buff: float = 20.0
    diona_C6_EM_value: float = 200.0
    diona_C6_stellar_damage_bonus: float = 40.0



    # 6. FARUZAN – C6
    atk_percent_vesna_a3_value_faruzan: float = 6
    faruzan_dps_value: float = 15000.0

    faruzan_anemo_res_reduction: float = 30.0
    faruzan_c6_anemo_crit_damage: float = 40.0
    faruzan_VV_set_cryo_res_reduction: float = 40.0

    faruzan_breezeborne_r1_stellar_damage_bonus: float = 24.0
    faruzan_breezeborne_r5_stellar_damage_bonus: float = 48.0 # auf r1


    # 7. SUCROSE – C6
    atk_percent_vesna_a3_value_sucrose: float = 6
    sucrose_total_em_value: float = 860.0
    sucrose_dps_value: float = 2500.0

    sucrose_instrcutor_team_buff_em_value: float = 120.0
    sucrose_talent_catalyst_conversion_bonus_em_value: float = 50.0
    sucrose_talent_mollis_favonius_em_value: float = 172.0

    #7.1 Cryo Lumine
    # C6 R5; Talents lv 10; 40 artifact stats; 75% CR +10%CR from anemo; 4 ER rolls +20% from Electro; +20% CD from Cryo
    # ATK Sands/Goblet; CR/CD Circlet
    # Sig weapon
    # Stats distribution rolls [ATK,ATK%,EM,CR%,CD%,ER%] [4,5,8,9,10,4]

    #Artifact Substat distribution profile:

    #Lumine Stats
    lumine_base_atk: float = 212
    lumine_sig_base_atk: float = 608
    lumine_base_atk_total: float = 820
    lumine_sig_base_cr_value: float = 33.1
    lumine_sig_CD_value: float = 42
    lumine_sig_atk_value: float = 40
    
    lumine_pyro_talent_atk_bonus: float = 20
    lumine_base_em_value: float = 280 #160 from talent + 60 from dendro + 60 from 100% uptime E Skill
    lumine_ascension_stat_atk_percent: float = 24

    #Stats from artifacts
    atk_2p2p_artifact_set_bonus: float = 36.0
    lumine_feather_flat_atk_bonus: float = 311
    lumine_artifact_sands_atk_value:float = 46.6
    lumine_artifact_goblet_atk_value:float = 46.6
    lumine_artifact_circlet_cd_value:float = 62.2

    lumine_total_em: float = 8*ARTIFACT_SUBSTATS["EM"]["average"]+ lumine_base_em_value
    lumine_total_CD: float = 10*ARTIFACT_SUBSTATS["CD%"]["average"] + lumine_sig_CD_value + lumine_artifact_circlet_cd_value

    # Lumine MV
    lumine_CA_mv: float = 253.3
    lumine_foreign_permafrost_stellar_CA_mv: float = 420
    lumine_mv_stellar_CA_mv_with_talent: float = 673.3

    lumine_mv_E_Skill_On_field_inital_mv_value: float = 217.74
    lumine_mv_E_Skill_off_field_periodic_mv_value: float = 50.81
    lumine_mv_E_Skill_off_fiel_periodic_tick_amount: float = 10

    lumine_stellar_Q_mv_value: float = 117.15
    lumine_number_of_Q_hits: float = 5
    
    lumine_frostglow_stellar_Q_mod: float = 5.86
    lumine_frostglow_stacks: float = 8
  

    lumine_ever_keen_frost_talent_atk_value: float = 80.0
    lumine_stellar_jubilee_talent_stellar_base_damage_mod: float = 14

    @property
    def lumine_frostfall_reverberation_em_bonus(self) -> float:
        return 60
    @property
    def lumine_frostfall_reverberation_em_bonus_after_stellar_damage(self) -> float:
        return 120

    @property
    def lumine_effective_cr(self) -> float:
        cr = 85.0

        # Apply team CR bonus
        if self.is_odette_active or self.is_diona_active:
            cr += 15.0

        return min(cr, 100.0)

    @property
    def lumine_crit_multiplier(self) -> float:
        crit_damage = self.lumine_total_CD

        return (
            1.0
            + (self.lumine_effective_cr / 100.0)
            * (crit_damage / 100.0)
        )

    @property
    def lumine_total_atk(self) -> float:
        vodyanitsa_c1_bonus = (self.vodyanitsa_C1_flat_atk_bonus if (self.is_vodyanitsa_active and self.vodyanitsa_constellation >= 1) else 0.0)

        return (
            self.lumine_base_atk_total
            * (
                1.0
                + (
                    self.lumine_sig_atk_value
                    + self.lumine_ascension_stat_atk_percent
                    + self.atk_2p2p_artifact_set_bonus
                    + self.lumine_pyro_talent_atk_bonus
                    + self.lumine_artifact_sands_atk_value
                    + self.lumine_artifact_goblet_atk_value
                ) / 100.0
            )
            + self.lumine_feather_flat_atk_bonus
            + vodyanitsa_c1_bonus
        )

    @property
    def lumine_atk_percent_value(self) -> float:
        return self.team_atk_percent_common_bonus("vesna") + self.team_atk_percent_variable_bonus("vesna", True)


    @property
    def lumine_on_field_atk(self) -> float:
        return (self.lumine_total_atk + self.lumine_base_atk_total * self.lumine_atk_percent_value)

    #7.1.1 Lumine Damage calcs for E CA Q
    # Damage Calc for Stellar CA
    @property
    def lumine_stellar_charge_attack_damage(self) -> float:
        damage = (
            self.lumine_on_field_atk
            * (self.lumine_mv_stellar_CA_mv_with_talent / 100.0)
            * self.calculate_stellar_damage_multiplier("lumine")
        )

        return (
            damage
            * self.calculate_stellar_crit_multiplier("lumine", "cryo")
            * self.calculate_cryo_res_multiplier
        )
    #Damage Calc for E-Skill
    @property
    def lumine_e_skill_cryo_damage_on_field(self) -> float:
        damage = (
            self.lumine_on_field_atk
            * (self.lumine_mv_E_Skill_On_field_inital_mv_value / 100.0)
        )

        return (
            damage
            * self.lumine_crit_multiplier
            * self.general_defense_multiplier_90
            * self.calculate_cryo_res_multiplier
        )

    #Damage Calc for E-Skill off-field
    @property
    def lumine_e_skill_cryo_damage_off_field(self) -> float:
        damage_per_tick = (self.lumine_total_atk* (self.lumine_mv_E_Skill_off_field_periodic_mv_value / 100.0))

        return (
            damage_per_tick
            * self.lumine_mv_E_Skill_off_fiel_periodic_tick_amount
            * self.lumine_crit_multiplier
            * self.general_defense_multiplier_90
            * self.calculate_cryo_res_multiplier
        )

    # Damage Calc for Stellar Q
    @property
    def lumine_ultimate_q_stellar_damage(self) -> float:
        total_mv = (
            self.lumine_stellar_Q_mv_value
            * self.lumine_number_of_Q_hits
        )

        frostglow_bonus = (
            self.lumine_frostglow_stellar_Q_mod
            * self.lumine_frostglow_stacks
        )

        damage = (
            self.lumine_on_field_atk
            * (total_mv / 100.0)
            * self.calculate_stellar_damage_multiplier("lumine")
            * (1.0 + frostglow_bonus / 100.0)
        )

        return (
            damage
            * self.calculate_stellar_crit_multiplier("lumine", "cryo")
            * self.calculate_cryo_res_multiplier
        )
    @property
    def lumine_rotation_damage(self) -> float:
        """Total damage dealt by Lumine during one rotation."""
        return (
            self.lumine_stellar_charge_attack_damage
            + self.lumine_e_skill_cryo_damage_on_field
            + self.lumine_e_skill_cryo_damage_off_field
            + self.lumine_ultimate_q_stellar_damage
        )

    # Anastasaya Stats
    # Signature Weappon
    # Stats distribution rolls [ATK,ATK%,EM,CR%,CD%,ER%] [4,5,5,12,12,2]
    # ER on weapon reduces req ER rolls by 2
    # we can say she is holidng her sig or breezeborne
    # I am assuming Anastasya has CD Ascension
    # Artifact Substat distribution profile:

    #Anastasya's  Stats
    anastasya_rotation_length: float = 20.5
    anastasya_base_atk: float = 350 #assumed, we dont know yet
    anastasya_base_atk_sig_base_atk: float = 674
    anastasya_base_atk_total: float = 1024
    anastasya_sig_CD_value: float = 44.1
    anastasya_sig_stellar_CD_value: float = 40.0
    anastasya_sig_atk_value: float = 40.0
    anastasya_base_em_value: float = 0.0
    anstasya_CD_ascension_value: float = 38.4

    # Tsaritsa Artifact Set
    tsaritsa_atk_bonus: float = 18.0
    tsaritsa_cryo_cr_bonus: float = 20.0
    tsaritsa_stellar_cr_bonus: float = 40.0

    
    #Anastasya's Stats from artifacts
    anastasya_feather_flat_atk_bonus: float = 311
    anastasya_artifact_sands_atk_value:float = 46.6
    anastasya_artifact_goblet_atk_value:float = 46.6
    anastasya_artifact_circlet_CD_value:float = 62.2

    anastasya_total_em: float = 5*ARTIFACT_SUBSTATS["EM"]["average"]
    anastasya_total_CD: float = 10*ARTIFACT_SUBSTATS["CD%"]["average"] + anastasya_artifact_circlet_CD_value + anstasya_CD_ascension_value + anastasya_sig_CD_value

    # Anastasya's Team buffs from Kit 
    anastasya_talent_glory_team_CD_buff: float = 12  #20sec uptime 100%
    anastasya_talent_glory_stacks_team_CD_buff: float = 4 #
    anastasya_talent_stellar_damage_mod: float = 50 #from Q 100% uptime 
    anastasya_talent_stellar_base_damage_mod: float = 14   


    # Anastasya MV (Support Style)
    # E-Skill
    anastasya_mv_Tap_E_Skill_On_field_inital_mv_value: float = 212.76 #cryo damage 118.2 lv1 10
    anastasya_mv_Tap_E_Skill_off_field_cryo_periodic_mv_value: float = 1152 #cryo damage 35.6 lv1 1 // 64.0 lv 10
    anastasya_mv_Tap_E_Skill_off_field_stellar_periodic_mv_value: float = 1080 #stellar damage 33.3 lv1 // 60.0 lv 10

    # Q-Ultimate
    anastasya_to_a_new_world_inital_cryo_Q_mv_value: float = 360.7 #cryo damage happens before she leaves the field
    anastasya_to_a_new_world_stellar_Q_mv_value: float = 601.2 #stellar damage happens on re entering the field
    anastasya_mv_off_field_stellar_periodic_mv_value_after_Q: float = 543.6 #stellar damage
    
    #C1
    anastasya_C1_cryo_character_atk_buff: float = 15.0
    anastasya_C1_not_cryo_character_em_buff: float = 60
    anastasya_C1_glory_team_CD_buff_multi: float = 3
    #C2
    anastasya_C2_stellar_elevation_mod: float = 1.05 #evelation is multiplied next to res multiplier at the end
    anastasya_C2_stellar_CD_mod: float = 60 #100% uptime

    @property
    def anastasya_effective_cr(self) -> float:
        cr = (5.0+ 12 * ARTIFACT_SUBSTATS["CR%"]["average"])

        # Apply team CR bonus
        if self.is_odette_active or self.is_diona_active or self.is_lumine_active:
            cr += 15.0

        # Apply Tsaritsa set CR bonus for cryo damage
        if self.active_team_artifact_set_distribution_and_buffs["tsaritsa"]["holder"] == "anastasya":
            cr += 20.0

        return min(cr, 100.0)
    @property
    def anastasya_effective_stellar_cr(self) -> float:
        cr = self.anastasya_effective_cr

        # Tsaritsa 4-piece CR bonus for Stellar Glimmer damage
        if self.active_team_artifact_set_distribution_and_buffs["tsaritsa"]["holder"] == "anastasya":
            cr += 40.0

        return min(cr, 100.0)
    @property
    def anastasya_cryo_crit_multiplier(self) -> float:
        crit_damage = self.anastasya_total_CD

        return (
            1.0
            + (self.anastasya_effective_cr / 100.0)
            * (crit_damage / 100.0)
        )

    @property
    def anastasya_stellar_crit_multiplier(self) -> float:
        crit_damage = self.anastasya_total_CD
        stellar_cr = self.anastasya_effective_stellar_cr

        return (
            1.0
            + (stellar_cr / 100.0)
            * (crit_damage / 100.0)
        )

    @property
    def anastasya_total_atk(self) -> float:
        vodyanitsa_c1_bonus = (self.vodyanitsa_C1_flat_atk_bonus if self.is_vodyanitsa_active and self.vodyanitsa_constellation >= 1 else 0.0)
        tsaritsa_atk_bonus = (self.active_team_artifact_set_distribution_and_buffs["tsaritsa"]["atk_bonus"]if self.active_team_artifact_set_distribution_and_buffs["tsaritsa"]["holder"] == "anastasya"else 0.0)

        return (
            self.anastasya_base_atk_total
            * (
                1.0
                + (
                    self.anastasya_sig_atk_value
                    + self.anastasya_artifact_sands_atk_value
                    + self.anastasya_artifact_goblet_atk_value
                    + tsaritsa_atk_bonus
                ) / 100.0
            )
            + self.anastasya_feather_flat_atk_bonus
            + vodyanitsa_c1_bonus
        )

    @property
    def anastasya_atk_percent_value(self) -> float:
        return (
            self.team_atk_percent_common_bonus("anastasya")
            + self.team_atk_percent_variable_bonus("anastasya", True)
        )

    @property
    def anastasya_on_field_atk(self) -> float:
        return (self.anastasya_total_atk + self.anastasya_base_atk_total * self.anastasya_atk_percent_value)
    @property
    def anastasya_off_field_atk(self) -> float:
        return (
            self.anastasya_total_atk
            + self.anastasya_base_atk_total
            * (
                self.team_atk_percent_common_bonus("anastasya")
                + self.team_atk_percent_variable_bonus("anastasya", False)
            )
        )
    # Anastasya Stellar Damage Calc
    def calculate_anastasya_stellar_damage(self, mv: float,atk: float,on_field: bool = True) -> float:
        damage = (
            atk
            * (mv / 100.0)
            * self.calculate_stellar_damage_multiplier(
                "anastasya",
                on_field=on_field,
            )
        )

        # Add Vodyanitsa Stellar Quills flat damage
        if not (self.is_odette_active and self.is_vodyanitsa_active):
            damage += self.active_vodyanitsa_stellar_quills_flat_damage

        return (
            damage
            * self.anastasya_stellar_crit_multiplier
            * self.calculate_cryo_res_multiplier
        )

    #Damage Calc for E-Skill
    @property
    def anastasya_e_skill_cryo_damage_on_field(self) -> float:
        damage = (
            self.anastasya_on_field_atk
            * (self.anastasya_mv_Tap_E_Skill_On_field_inital_mv_value / 100.0)
        )

        return (
            damage
            * self.anastasya_cryo_crit_multiplier
            * self.general_defense_multiplier_90
            * self.calculate_cryo_res_multiplier
        )

    #Damage Calc for E-Skill off-field
    @property
    def anastasya_e_skill_cryo_damage_off_field(self) -> float:
        damage_per_tick = self.anastasya_off_field_atk * (self.anastasya_mv_Tap_E_Skill_off_field_cryo_periodic_mv_value / 100.0)

        return (
            damage_per_tick
            * self.anastasya_cryo_crit_multiplier
            * self.general_defense_multiplier_90
            * self.calculate_cryo_res_multiplier
        )

    # Damage Calc for E-Skill off-field Stellar
    @property
    def anastasya_e_skill_stellar_damage_off_field(self) -> float:
        return self.calculate_anastasya_stellar_damage(
            mv=self.anastasya_mv_Tap_E_Skill_off_field_stellar_periodic_mv_value,
            atk=self.anastasya_off_field_atk,
            on_field=False,
        )
    # Damage Calc for Cryo Q
    @property
    def anastasya_ultimate_q_cryo_damage_on_field(self) -> float:
        damage = (
            self.anastasya_on_field_atk
            * (self.anastasya_to_a_new_world_inital_cryo_Q_mv_value / 100.0)
        )

        return (
            damage
            * self.anastasya_cryo_crit_multiplier
            * self.general_defense_multiplier_90
            * self.calculate_cryo_res_multiplier
        )
    # Damage Calc for Stellar Q
    @property
    def anastasya_ultimate_q_stellar_damage(self) -> float:
        total_mv = (self.anastasya_to_a_new_world_stellar_Q_mv_value)

        return self.calculate_anastasya_stellar_damage(
            mv=total_mv,
            atk=self.anastasya_on_field_atk,
            on_field=True,
        )
    # Damage Calc for Stellar Q Off-Field Tick
    @property
    def anastasya_ultimate_q_stellar_damage_off_field_tick_damage(self) -> float:
        return self.calculate_anastasya_stellar_damage(
            mv=self.anastasya_mv_off_field_stellar_periodic_mv_value_after_Q,
            atk=self.anastasya_off_field_atk,
            on_field=False,
        )
    @property
    def anastasya_rotation_damage(self) -> float:
        """Total damage dealt by Anastasya during one rotation."""
        return (
            + self.anastasya_e_skill_cryo_damage_on_field
            + self.anastasya_e_skill_cryo_damage_off_field
            + self.anastasya_e_skill_stellar_damage_off_field
            + self.anastasya_ultimate_q_stellar_damage
            + self.anastasya_ultimate_q_stellar_damage_off_field_tick_damage
            + self.anastasya_ultimate_q_cryo_damage_on_field
        )

    # 8. VESNA – STATS AND DAMAGE MULTIPLIERS
    @property
    def vesna_atk_percent_value(self) -> float:
        return (
            self.atk_percent_sands
            + self.atk_percent_goblet
            + self.atk_percent_set_bonus
            + self.atk_percent
            + (self.atk_percent_vesna_a3_talent_cryo_anemo_trio if self.is_vodyanitsa_active else self.atk_percent_vesna_a3_talent_cryo_anemo_quartett)
        ) / 100.0 + self.team_atk_percent_common_bonus("vesna") + self.team_atk_percent_variable_bonus("vesna", True)

    @property
    def vesna_base_atk_value(self) -> float:
        if self.level == self.vesna_level_90:
            return self.base_atk_lv_90
        elif self.level == self.vesna_level_95:
            return self.base_atk_lv_95

        raise ValueError(f"Unsupported Vesna level: {self.level}")

    @property
    def vesna_total_atk_value(self) -> float:
        vodyanitsa_c1_bonus = (self.vodyanitsa_C1_flat_atk_bonus
            if (self.is_vodyanitsa_active and self.vodyanitsa_constellation >= 1) else 0.0)

        return (
            self.vesna_base_atk_value
            * (1.0 + self.vesna_atk_percent_value)
            + self.vesna_flat_atk_feather
            + self.flat_attack_value
            + vodyanitsa_c1_bonus
        )

    @property
    def vesna_em_value(self) -> float:
        return (
            self.vesna_base_em
            + self.elemental_mastery
            + self.team_em_buff("vesna")
        )

    @property
    def vesna_crit_damage_value(self) -> float:
        return (
            self.crit_damage_base
            + self.crit_damage_circlet
            + self.crit_damage_signature
            + self.crit_damage
            + self.weapon_proc_crit_damage
        )

    @property
    def vesna_anemo_crit_multiplier(self) -> float:
        crit_damage = self.vesna_crit_damage_value

        if self.is_faruzan_active:
            crit_damage += self.faruzan_c6_anemo_crit_damage

        return 1.0 + crit_damage / 100.0

    # 8.1 Vesna damage calcs
    def calculate_anemo_damage_lv90(self) -> float:
        return (
            self.vesna_total_atk_value
            * (self.anemo_mv / 100.0)
            * self.vesna_anemo_crit_multiplier
            * self.general_defense_multiplier_90
            * self.calculate_anemo_res_multiplier
        )
    def calculate_anemo_damage_lv95(self) -> float:
        return (
            self.vesna_total_atk_value
            * (self.anemo_mv / 100.0)
            * self.vesna_anemo_crit_multiplier
            * self.general_defense_multiplier_95
            * self.calculate_anemo_res_multiplier
        )
    @property
    def vesna_total_stellar_damage(self) -> float:
        total_atk = self.vesna_total_atk_value

        # Vesna C2 additional ATK
        if self.vesna_constellation >= 2.0:
            total_atk += (
                self.vesna_base_atk_value
                * (1.0 + self.vesna_atk_percent_value)
                * self.vesna_C2_atk_value
                / 100.0
            )

        e_damage_mv = self.e_stellar_mv

        # Determine Stellar multipliers
        se1_multiplier = (
            self.se_stage_0_multiplier
            if self.vesna_constellation >= 2.0
            else self.se1_stage_damage_multiplier
        )
        se2_multiplier = (
            self.se_stage_0_multiplier
            if self.vesna_constellation >= 2.0
            else self.se2_stage_damage_multiplier
        )
        q_multiplier = (
            self.se_stage_0_multiplier
            if self.vesna_constellation >= 2.0
            else self.stellar_Q_damage_multiplier
        )

        se1_damage_mv = self.se1_stellar_mv * se1_multiplier
        se2_damage_mv = self.se2_stellar_mv * se2_multiplier
        q_damage_mv = self.stellar_Q_damage_MV * q_multiplier

        se3_stage1_multiplier = (
            self.se_stage_0_multiplier
            if self.vesna_constellation >= 2.0
            else self.se3_stage1_multiplier
        )
        se3_stage2_multiplier = (
            self.se_stage_0_multiplier
            if self.vesna_constellation >= 2.0
            else self.se3_stage2_multiplier
        )
        se3_stage3_multiplier = (
            self.se_stage_0_multiplier
            if self.vesna_constellation >= 2.0
            else self.se3_stage3_multiplier
        )

        se3_base_mv = (
            self.se3_spirit_mv * self.se3_spirit_hits
            + self.se3_final_mv
        )

        total_mv = (
            e_damage_mv
            + se1_damage_mv
            + se2_damage_mv
            + q_damage_mv
            + se3_base_mv * se3_stage1_multiplier
            + se3_base_mv * se3_stage2_multiplier
            + se3_base_mv * se3_stage3_multiplier
        )

        # Vesna C1 additional Stellar damage
        if self.vesna_constellation >= 1.0:
            total_mv += self.vesna_C1_additional_stellar_mv

        damage = (
            total_atk
            * (total_mv / 100.0)
            * self.calculate_stellar_damage_multiplier("vesna")
        )

        # Add Vodyanitsa Stellar Quills flat damage
        damage += self.active_vodyanitsa_stellar_quills_flat_damage

        return (
            damage
            * self.calculate_stellar_crit_multiplier("vesna", "anemo")
            * self.calculate_anemo_res_multiplier
        )

    def calculate_vortex_proc_damage(self) -> float:
        if self.level == self.vesna_level_90:
            level_modifier = self.lv90_modifier
        elif self.level == self.vesna_level_95:
            level_modifier = self.lv95_modifier
        else:
            raise ValueError(f"Unsupported Vesna level: {self.level}")

        damage = (
            level_modifier
            * 0.75
            * 0.6
            * self.calculate_stellar_damage_multiplier("vesna")
        )

        # Add Vodyanitsa Stellar Quills flat damage
        damage += self.active_vodyanitsa_stellar_quills_flat_damage

        return (
            damage
            * self.calculate_stellar_crit_multiplier("vesna", "anemo")
            * self.calculate_anemo_res_multiplier
        )
    def calculate_vortex_explosion_damage(self) -> float:
        if self.level == self.vesna_level_90:
            level_modifier = self.lv90_modifier
        elif self.level == self.vesna_level_95:
            level_modifier = self.lv95_modifier
        else:
            raise ValueError(f"Unsupported Vesna level: {self.level}")

        damage = (
            level_modifier
            * 3.0
            * 0.3
            * self.calculate_stellar_damage_multiplier("odette", on_field=False)
        )
        # Add Vodyanitsa Stellar Quills flat damage
        damage += self.active_vodyanitsa_stellar_quills_flat_damage
        return (
            damage
            * self.calculate_stellar_crit_multiplier("odette", "cryo")
            * self.calculate_cryo_res_multiplier
        )
        
    def calculate_vesna_total_vortex_damage(self) -> float:
        proc_damage = self.calculate_vortex_proc_damage()
        explosion_damage = self.calculate_vortex_explosion_damage()

        return (
            proc_damage * self.vortex_procs
            + explosion_damage * self.vortex_explosions
        )   

    def calculate_total_vesna_damage(self, verbose: bool = False) -> float:
        anemo_damage = self.calculate_anemo_damage_lv90()
        stellar_damage = self.vesna_total_stellar_damage
        vortex_damage = self.calculate_vesna_total_vortex_damage()

        total_damage = (
            anemo_damage
            + stellar_damage
            + vortex_damage
        )

        if verbose:
            print(f"Anemo Damage:   {anemo_damage:,.2f}")
            print(f"Stellar Damage: {stellar_damage:,.2f}")
            print(f"Vortex Damage:  {vortex_damage:,.2f}")
            print(f"Total Damage:   {total_damage:,.2f}")

        return total_damage
    

    # 12. TEAM CONFIGURATIONS AND CONSTELLATIONS
    @property
    def active_team(self) -> dict:
        team_name = self.current_configuration.get("team_name", self.team_name)

        for team in self.TEAMS:
            if team["name"] == team_name:
                return team

        raise ValueError(f"Unknown team: {team_name}")

    @property
    def active_team_members(self) -> list[str]:
        return self.active_team["members"]

    # 8. Team Comps and definitions
    TEAMS: ClassVar[list[dict]] = [
        # {"name": "Vesna_Odette_Vodyanitsa_Faruzan",
        #  "members": ["vesna", "odette", "vodyanitsa", "faruzan"]},

        # {"name": "Vesna_Odette_Vodyanitsa_Diona",
        #  "members": ["vesna", "odette", "vodyanitsa", "diona"]},

        # {"name": "Vesna_Odette_Vodyanitsa_Sucrose",
        #  "members": ["vesna", "odette", "vodyanitsa", "sucrose"]},

        # {"name": "Vesna_Odette_Faruzan_Diona",
        #  "members": ["vesna", "odette", "faruzan", "diona"]},

        # {"name": "Vesna_Odette_Faruzan_Sucrose",
        #  "members": ["vesna", "odette", "faruzan", "sucrose"]},

        # {"name": "Vesna_Vodyanitsa_Faruzan_Diona",
        #  "members": ["vesna", "vodyanitsa", "faruzan", "diona"]},

        # {"name": "Vesna_Vodyanitsa_Faruzan_Sucrose",
        #  "members": ["vesna", "vodyanitsa", "faruzan", "sucrose"]},

        # {"name": "Vesna_Odette_Diona_Sucrose",
        #  "members": ["vesna", "odette", "diona", "sucrose"]},

        # {"name": "Vesna_Vodyanitsa_Diona_Sucrose",
        #  "members": ["vesna", "vodyanitsa", "diona", "sucrose"]},

        # {"name": "Vesna_Faruzan_Diona_Sucrose",
        #  "members": ["vesna", "faruzan", "diona", "sucrose"]},

        # {"name": "Vesna_Odette_Vodyanitsa_Lumine",
        #  "members": ["vesna", "odette", "vodyanitsa", "lumine"]},

        # {"name": "Vesna_Odette_Faruzan_Lumine",
        #  "members": ["vesna", "odette", "faruzan", "lumine"]},

        # {"name": "Vesna_Odette_Diona_Lumine",
        #  "members": ["vesna", "odette", "diona", "lumine"]},

        # {"name": "Vesna_Odette_Sucrose_Lumine",
        #  "members": ["vesna", "odette", "sucrose", "lumine"]},

        # {"name": "Vesna_Vodyanitsa_Faruzan_Lumine",
        #  "members": ["vesna", "vodyanitsa", "faruzan", "lumine"]},

        # {"name": "Vesna_Vodyanitsa_Diona_Lumine",
        #  "members": ["vesna", "vodyanitsa", "diona", "lumine"]},

        # {"name": "Vesna_Vodyanitsa_Sucrose_Lumine",
        #  "members": ["vesna", "vodyanitsa", "sucrose", "lumine"]},

        # {"name": "Vesna_Faruzan_Diona_Lumine",
        #  "members": ["vesna", "faruzan", "diona", "lumine"]},

        # {"name": "Vesna_Faruzan_Sucrose_Lumine",
        #  "members": ["vesna", "faruzan", "sucrose", "lumine"]},

        # {"name": "Vesna_Diona_Sucrose_Lumine",
        #  "members": ["vesna", "diona", "sucrose", "lumine"]},
        # Anastasya Teams
        {"name": "Vesna_Anastasya_Odette_Vodyanitsa",
        "members": ["vesna", "anastasya", "odette", "vodyanitsa"]},

        {"name": "Vesna_Anastasya_Odette_Faruzan",
        "members": ["vesna", "anastasya", "odette", "faruzan"]},

        {"name": "Vesna_Anastasya_Odette_Diona",
        "members": ["vesna", "anastasya", "odette", "diona"]},

        {"name": "Vesna_Anastasya_Odette_Sucrose",
        "members": ["vesna", "anastasya", "odette", "sucrose"]},

        {"name": "Vesna_Anastasya_Odette_Lumine",
        "members": ["vesna", "anastasya", "odette", "lumine"]},

        {"name": "Vesna_Anastasya_Vodyanitsa_Faruzan",
        "members": ["vesna", "anastasya", "vodyanitsa", "faruzan"]},

        {"name": "Vesna_Anastasya_Vodyanitsa_Diona",
        "members": ["vesna", "anastasya", "vodyanitsa", "diona"]},

        {"name": "Vesna_Anastasya_Vodyanitsa_Sucrose",
        "members": ["vesna", "anastasya", "vodyanitsa", "sucrose"]},

        {"name": "Vesna_Anastasya_Vodyanitsa_Lumine",
        "members": ["vesna", "anastasya", "vodyanitsa", "lumine"]},

        {"name": "Vesna_Anastasya_Faruzan_Diona",
        "members": ["vesna", "anastasya", "faruzan", "diona"]},

        {"name": "Vesna_Anastasya_Faruzan_Sucrose",
        "members": ["vesna", "anastasya", "faruzan", "sucrose"]},

        {"name": "Vesna_Anastasya_Faruzan_Lumine",
        "members": ["vesna", "anastasya", "faruzan", "lumine"]},

        {"name": "Vesna_Anastasya_Diona_Sucrose",
        "members": ["vesna", "anastasya", "diona", "sucrose"]},

        {"name": "Vesna_Anastasya_Diona_Lumine",
        "members": ["vesna", "anastasya", "diona", "lumine"]},

        {"name": "Vesna_Anastasya_Sucrose_Lumine",
        "members": ["vesna", "anastasya", "sucrose", "lumine"]},
    ]
    VESNA_CONSTELLATIONS: ClassVar[list[float]] = [0.0, 1.0, 2.0]
    ODETTE_CONSTELLATIONS: ClassVar[list[float]] = [0.0, 1.0, 2.0]
    VODYANITSA_CONSTELLATIONS: ClassVar[list[float]] = [0.0, 1.0, 2.0]
    ANASTASYA_CONSTELLATIONS: ClassVar[list[float]] = [0.0, 1.0, 2.0]

    team_name: str = "Vesna_Odette_Vodyanitsa_Faruzan"
    current_configuration: dict = field(default_factory=dict)
    @property  # Include every team configuration
    def all_team_configurations(self) -> list[dict]:
        configurations = []

        constellation_options = {
            "vesna": self.VESNA_CONSTELLATIONS,
            "odette": self.ODETTE_CONSTELLATIONS,
            "anastasya": self.ANASTASYA_CONSTELLATIONS,
            "vodyanitsa": self.VODYANITSA_CONSTELLATIONS,
        }

        for team in self.TEAMS:
            members = team["members"]

            variable_members = [
                member
                for member in ("vesna", "odette", "anastasya", "vodyanitsa")
                if member in members
            ]

            options = [
                constellation_options[member]
                for member in variable_members
            ]

            for values in product(*options):
                constellations = dict(zip(variable_members, values))

                for member in members:
                    if member in ("diona", "faruzan", "sucrose"):
                        constellations[member] = 6

                configurations.append({
                    "name": f"Team_Comp_{len(configurations) + 1:03d}_calced",
                    "team_name": team["name"],
                    "members": members.copy(),
                    "constellations": constellations.copy(),
                })

        return configurations


@dataclass
class VesnaDPSTheoryExport:
    configuration: int
    team_name: str
    configuration_name: str
    line_type: str

    vesna_constellation: int
    odette_constellation: int
    vodyanitsa_constellation: int
    anastasya_constellation: int

    artifact_sets: dict[str, str | None]

    best_profile: tuple[int, int, int, int, int, int]

    vesna_rotation_damage: float
    vesna_dps: float

    odette_rotation_damage: float
    odette_dps: float

    lumine_dps: float
    diona_dps: float
    faruzan_dps: float
    sucrose_dps: float
    vodyanitsa_dps: float

    rotation_duration: float
    team_rotation_damage: float
    team_dps: float

    @classmethod
    def export_to_excel(
        cls,
        results: list["VesnaDPSTheoryExport"],
        output_path: str = "vesna_team_dps.xlsx",
    ) -> None:

        if not results:
            raise ValueError("No export results available.")

        wb = Workbook()

        # ----------------------------------------------------
        # Configurations
        # ----------------------------------------------------


        ws = wb.active
        ws.title = "Configurations"

        profile_names = [
            "profile_flat_atk_rolls",
            "profile_atk_percent_rolls",
            "profile_cd_percent_rolls",
            "profile_em_rolls",
            "profile_cr_percent_rolls",
            "profile_er_percent_rolls",
        ]

        artifact_names = [
            f"artifact_{key}"
            for key in results[0].artifact_sets.keys()
        ]

        headers = [
            key
            for key in asdict(results[0]).keys()
            if key not in ("artifact_sets", "best_profile")
        ]

        headers.extend(artifact_names)
        headers.extend(profile_names)

        ws.append(headers)

        for result in results:
            row = asdict(result)

            artifact_sets = row.pop("artifact_sets")
            best_profile = row.pop("best_profile")

            row.update({
                f"artifact_{key}": value
                for key, value in artifact_sets.items()
            })

            row.update(dict(zip(profile_names, best_profile)))

            ws.append([
                row.get(header)
                for header in headers
            ])


        # ----------------------------------------------------
        # Ranking
        # ----------------------------------------------------

        ranking = wb.create_sheet("Ranking")

        ranking_headers = [
            "Rank",
            "Configuration",
            "Team",
            "Line Type",
            "Team Rotation Damage",
            "Rotation Duration",
            "Team DPS",
        ]

        ranking.append(ranking_headers)

        sorted_results = sorted(
            results,
            key=lambda item: item.team_dps,
            reverse=True,
        )

        for rank, result in enumerate(sorted_results, start=1):
            ranking.append([
                rank,
                result.configuration,
                result.team_name,
                result.line_type,
                result.team_rotation_damage,
                result.rotation_duration,
                result.team_dps,
            ])

        # ----------------------------------------------------
        # Analysis
        # ----------------------------------------------------

        analysis = wb.create_sheet("Analysis")

        analysis.append(["Metric", "Value"])
        analysis.append(["Total Configurations", len(results)])

        dps_values = [result.team_dps for result in results]

        analysis.append([
            "Average Team DPS",
            sum(dps_values) / len(dps_values),
        ])

        analysis.append(["Highest Team DPS", max(dps_values)])
        analysis.append(["Lowest Team DPS", min(dps_values)])

        best_result = max(
            results,
            key=lambda item: item.team_dps,
        )

        analysis.append([
            "Best Configuration",
            best_result.configuration,
        ])

        analysis.append([
            "Best Team",
            best_result.team_name,
        ])

        # ----------------------------------------------------
        # Formatting
        # ----------------------------------------------------

        for sheet in wb.worksheets:
            sheet.freeze_panes = "B2"
            sheet.auto_filter.ref = sheet.dimensions

            for cell in sheet[1]:
                cell.font = Font(
                    bold=True,
                    color="FFFFFF",
                )
                cell.fill = PatternFill(
                    "solid",
                    fgColor="1F4E78",
                )
                cell.alignment = Alignment(
                    horizontal="center",
                )

            for column in sheet.columns:
                column_letter = get_column_letter(
                    column[0].column
                )

                max_length = max(
                    (
                        len(str(cell.value))
                        for cell in column
                        if cell.value is not None
                    ),
                    default=10,
                )

                sheet.column_dimensions[column_letter].width = min(
                    max_length + 2,
                    32,
                )

        # Highlight team DPS values.
        for sheet_name, column_name in [
            ("Configurations", "team_dps"),
            ("Ranking", "Team DPS"),
        ]:
            sheet = wb[sheet_name]

            headers = [
                cell.value
                for cell in sheet[1]
            ]

            if column_name in headers:
                column_index = headers.index(column_name) + 1
                column_letter = get_column_letter(column_index)

                sheet.conditional_formatting.add(
                    f"{column_letter}2:{column_letter}{sheet.max_row}",
                    ColorScaleRule(
                        start_type="min",
                        start_color="F8696B",
                        mid_type="percentile",
                        mid_value=50,
                        mid_color="FFEB84",
                        end_type="max",
                        end_color="63BE7B",
                    ),
                )

        wb.save(Path(output_path))

# COMBINATORICS: GENERATE DISTRIBUTIONS
def calculate_distributions(line_type):
    """
    Generates aggregated distributions of all substat rolls.

    ER% is fixed at 2 rolls.
    CR% is fixed at 11 rolls.
    The remaining rolls are distributed among the other substats.
    """

    if line_type not in DISTRIBUTION_CONFIG:
        raise ValueError(f"Unknown artifact type: {line_type}")

    config = DISTRIBUTION_CONFIG[line_type]
    total_rolls = config["total_rolls"]
    reserved = config["reserved_rolls"]

    suffix = "3line" if line_type == "3_line" else "4line"

    # CR% and ER% are fixed and are no longer treated as variable distribution dimensions.
    fixed_stats = {
        "CR%": 11,
        "ER%": 2,
    }

    for stat, amount in fixed_stats.items():
        if reserved.get(stat, 0) != amount:
            raise ValueError(
                f"{stat} must be fixed at {amount} rolls."
            )

    stats = [
        stat for stat in ARTIFACT_SUBSTATS
        if stat not in fixed_stats
    ]

    max_rolls = {
        stat: data[f"max_{suffix}"]
        for stat, data in ARTIFACT_SUBSTATS.items()
    }

    initial = {
        stat: fixed_stats.get(stat, 0)
        for stat in ARTIFACT_SUBSTATS
    }

    for stat, amount in fixed_stats.items():
        if amount > max_rolls[stat]:
            raise ValueError(
                f"Reservation for {stat} exceeds the limit."
            )

    free_rolls = total_rolls - sum(fixed_stats.values())

    if free_rolls < 0:
        raise ValueError("Reserved rolls exceed the total budget.")

    remaining_caps = {
        stat: max_rolls[stat]
        for stat in stats
    }

    if sum(remaining_caps.values()) < free_rolls:
        raise ValueError("The substat limits are insufficient for the roll budget.")

    def generate(index, remaining, current):
        if index == len(stats):
            if remaining == 0:
                yield current.copy()
            return

        stat = stats[index]
        max_additional = min(remaining, remaining_caps[stat])

        for amount in range(max_additional + 1):
            current[stat] = amount

            yield from generate(
                index + 1,
                remaining - amount,
                current,
            )

        current[stat] = 0

    yield from generate(0, free_rolls, initial.copy())
def calculate_relevant_distributions(line_type):
    """
    Generates only distinct damage-relevant roll distributions.

    CR% and ER% are fixed.
    HP, HP%, DEF, and DEF% are not distributed individually
    because they do not affect Vesna's current damage.

    The global roll capacity of these irrelevant stats
    is still taken into account.
    """

    if line_type not in DISTRIBUTION_CONFIG:
        raise ValueError(f"Unknown artifact type: {line_type}")

    config = DISTRIBUTION_CONFIG[line_type]
    total_rolls = config["total_rolls"]
    suffix = "3line" if line_type == "3_line" else "4line"

    fixed_stats = {
        "CR%": 11,
        "ER%": 2,
    }

    for stat, amount in fixed_stats.items():
        if config["reserved_rolls"].get(stat, 0) != amount:
            raise ValueError(
                f"{stat} must be fixed at {amount} rolls."
            )

        if amount > ARTIFACT_SUBSTATS[stat][f"max_{suffix}"]:
            raise ValueError(
                f"Reservation for {stat} exceeds the limit."
            )

    relevant_stats = ["ATK", "ATK%", "CD%", "EM"]

    irrelevant_stats = [
        stat for stat in ARTIFACT_SUBSTATS
        if stat not in relevant_stats
        and stat not in fixed_stats
    ]

    free_rolls = total_rolls - sum(fixed_stats.values())

    relevant_caps = {
        stat: ARTIFACT_SUBSTATS[stat][f"max_{suffix}"]
        for stat in relevant_stats
    }

    irrelevant_capacity = sum(
        ARTIFACT_SUBSTATS[stat][f"max_{suffix}"]
        for stat in irrelevant_stats
    )

    current = fixed_stats.copy()

    for stat in relevant_stats:
        current[stat] = 0

    def generate(index, remaining):
        if index == len(relevant_stats):
            # The remaining rolls must fit within the capacity of the irrelevant stats.
            if 0 <= remaining <= irrelevant_capacity:
                yield current.copy()
            return

        stat = relevant_stats[index]
        max_amount = min(remaining, relevant_caps[stat])

        for amount in range(max_amount + 1):
            current[stat] = amount

            yield from generate(
                index + 1,
                remaining - amount,
            )

        current[stat] = 0

    yield from generate(0, free_rolls)
def generate_artifact_profiles(main_stat, line_type):
    """
    Generates possible substat roll profiles for a single artifact.

    3_line:
        3 initial substats, a fourth substat at +4,
        followed by 5 upgrades across the four substats.

    4_line:
        4 initial substats and 5 upgrades across the four substats.
    """
    if line_type not in ("3_line", "4_line"):
        raise ValueError(f"Unknown line type: {line_type}")

    available_stats = [
        stat for stat in ARTIFACT_SUBSTATS
        if stat != main_stat
    ]

    initial_line_count = 3 if line_type == "3_line" else 4
    profiles = set()

    for initial_stats in combinations(
        available_stats, initial_line_count
    ):
        if line_type == "3_line":
            fourth_stats = [
                stat for stat in available_stats
                if stat not in initial_stats
            ]
        else:
            fourth_stats = [None]

        for fourth_stat in fourth_stats:
            lines = list(initial_stats)

            if fourth_stat is not None:
                lines.append(fourth_stat)

            # 3 line Artifacts 4 total upgrad + fourth stat
            # 4 Line Artifacts 5 total upgrades
            upgrade_count = 4 if line_type == "3_line" else 5

            counts = {stat: 0 for stat in ARTIFACT_SUBSTATS}
            for stat in lines:
                counts[stat] += 1

            def distribute(index, remaining):
                if index == len(lines):
                    if remaining == 0:
                        profiles.add(tuple(
                            counts[stat]
                            for stat in ARTIFACT_SUBSTATS
                        ))
                    return

                stat = lines[index]

                for amount in range(remaining + 1):
                    counts[stat] += amount
                    distribute(index + 1, remaining - amount)
                    counts[stat] -= amount

            distribute(0, upgrade_count)

    return profiles
ARTIFACT_SLOTS = {
    "flower": "HP",
    "feather": "ATK",
    "sands": "ATK%",
    "goblet": "ATK%",
    "circlet": "CD%",
}

def generate_relevant_artifact_profiles(main_stat, line_type):
    """
    Generates deduplicated artifact profiles containing only the
    damage-relevant and reserved substats.

    The following are stored:
    ATK, ATK%, CD%, EM, CR%, ER%.

    HP, HP%, DEF, and DEF% are ignored.
    """
    relevant_stats = ("ATK", "ATK%", "CD%", "EM", "CR%", "ER%")

    profiles = generate_artifact_profiles(main_stat, line_type)

    stat_order = list(ARTIFACT_SUBSTATS)
    relevant_indices = [
        stat_order.index(stat)
        for stat in relevant_stats
    ]

    relevant_profiles = {
        tuple(profile[index] for index in relevant_indices)
        for profile in profiles
    }

    return relevant_profiles
def calculate_combined_relevant_profiles(line_type):
    """
    Combines five artifacts pairwise.
    Profile order: ATK, ATK%, CD%, EM, CR%, ER%.
    """
    relevant_stats = ("ATK", "ATK%", "CD%", "EM", "CR%", "ER%")
    fixed_stats = {"CR%": 11, "ER%": 2}
    suffix = "3line" if line_type == "3_line" else "4line"
    total_rolls = DISTRIBUTION_CONFIG[line_type]["total_rolls"]

    caps = tuple(
        ARTIFACT_SUBSTATS[s][f"max_{suffix}"]
        for s in relevant_stats
    )

    irrelevant_stats = [
        s for s in ARTIFACT_SUBSTATS if s not in relevant_stats
    ]
    irrelevant_capacity = sum(
        ARTIFACT_SUBSTATS[s][f"max_{suffix}"]
        for s in irrelevant_stats
    )

    
    
    
    def combine_profiles(left_profiles, right_profiles):
        result = set()
        checked = 0
        progress_interval = 1_000_000

        # Rechte Profile nach CR-/ER-Rolls gruppieren.
        right_by_cr_er = {}
        for right in right_profiles:
            key = (right[4], right[5])
            right_by_cr_er.setdefault(key, []).append(right)

        for left in left_profiles:
            max_cr = fixed_stats["CR%"] - left[4]
            max_er = fixed_stats["ER%"] - left[5]

            if max_cr < 0 or max_er < 0:
                continue

            for cr in range(max_cr + 1):
                for er in range(max_er + 1):
                    for right in right_by_cr_er.get((cr, er), ()):
                        checked += 1
                        if checked % progress_interval == 0:
                            print(".", end="", flush=True)

                        # ATK, ATK%, CD% und EM frühzeitig begrenzen.
                        if left[0] + right[0] > caps[0]:
                            continue
                        if left[1] + right[1] > caps[1]:
                            continue
                        if left[2] + right[2] > caps[2]:
                            continue
                        if left[3] + right[3] > caps[3]:
                            continue

                        candidate = (
                            left[0] + right[0],
                            left[1] + right[1],
                            left[2] + right[2],
                            left[3] + right[3],
                            left[4] + right[4],
                            left[5] + right[5],
                        )

                        if sum(candidate) > total_rolls:
                            continue

                        result.add(candidate)

        print(
            f"\nChecked: {checked:,} combinations | "
            f"Valid profiles: {len(result):,}"
        )

        return result

    # Einzelprofile für jeden Platz vorberechnen.
    slot_profiles = {
        slot: generate_relevant_artifact_profiles(main_stat, line_type)
        for slot, main_stat in ARTIFACT_SLOTS.items()
    }

    # Zwei Paare bilden.
    flower_feather = combine_profiles(
        slot_profiles["flower"],
        slot_profiles["feather"],
    )
    print(f"Flower + Feather: {len(flower_feather):,}")

    sands_goblet = combine_profiles(
        slot_profiles["sands"],
        slot_profiles["goblet"],
    )
    print(f"Sands + Goblet: {len(sands_goblet):,}")

    # Paare kombinieren und mit der Krone abschließen.
    paired_profiles = combine_profiles(
        flower_feather,
        sands_goblet,
    )
    print(f"Four artifacts: {len(paired_profiles):,}")

    combined_profiles = combine_profiles(
        paired_profiles,
        slot_profiles["circlet"],
    )
    print(
    f"Five artifacts before final validation: "
    f"{len(combined_profiles):,}"
    )
    
    # Exakte CR-/ER-Rolls und genügend Platz für irrelevante Rolls.
    valid_profiles = {
        profile for profile in combined_profiles
        if profile[4] == fixed_stats["CR%"]
        and profile[5] == fixed_stats["ER%"]
        and total_rolls - sum(profile) <= irrelevant_capacity
    }

    return valid_profiles
def load_or_calculate_profiles(line_type):
    cache_file = Path(__file__).with_name(
        f"vesna_profiles_v1_{line_type}.json"  # v1: 14 CR rolls; v2: 11 CR rolls
    )

    # Load existing cache
    if cache_file.exists():
        with cache_file.open("r", encoding="utf-8") as file:
            profiles = {
                tuple(profile)
                for profile in json.load(file)
            }

        print(
            f"Profile cache loaded: {cache_file.name} "
            f"({len(profiles):,} profiles)"
        )
        return profiles

    # Cache does not exist yet: calculate profiles
    print("No profile cache found. Calculating profiles...")
    profiles = calculate_combined_relevant_profiles(line_type)

    # Convert profiles to lists for JSON serialization and save
    with cache_file.open("w", encoding="utf-8") as file:
        json.dump(
            sorted(profiles),
            file,
            separators=(",", ":")
        )

    print(f"Profile cache saved: {cache_file.name}")
    return profiles


def find_best_dps_profile(profiles, line_type, team_config, configuration):
    """
    Finds the best artifact profile for a given team configuration.

    Profile order:
    ATK, ATK%, CD%, EM, CR%, ER%
    """
    best_profile = None
    best_dps = float("-inf")

    roll_averages = {
        stat: ARTIFACT_SUBSTATS[stat]["average"]
        for stat in ("ATK", "ATK%", "CD%", "EM", "CR%", "ER%")
    }

    for index, profile in enumerate(profiles, start=1):
        (
            atk_rolls,
            atk_percent_rolls,
            cd_rolls,
            em_rolls,
            cr_rolls,
            er_rolls,
        ) = profile
        base_crit_rate = (24.2+ cr_rolls * ARTIFACT_SUBSTATS["CR%"]["average"])
        if ("diona" in team_config["members"] and "odette" in team_config["members"]):
            crit_rate = min(100.0, base_crit_rate + 30.8)
        else:
            crit_rate = min(85.0, base_crit_rate + 15.8)

        vesna = VesnaTeamDPSTheory(
            flat_attack_value=atk_rolls * roll_averages["ATK"],
            atk_percent=(atk_percent_rolls* ARTIFACT_SUBSTATS["ATK%"]["average"]),
            crit_damage=(cd_rolls* ARTIFACT_SUBSTATS["CD%"]["average"]),
            elemental_mastery=em_rolls * roll_averages["EM"],
            crit_rate=crit_rate / 100.0,
            energy_recharge=(er_rolls * ARTIFACT_SUBSTATS["ER%"]["average"]),
            team_name=team_config["team_name"],
            current_configuration=team_config.copy(),
        )
        rotation_time = vesna.rotation_duration
        total_damage = vesna.calculate_total_vesna_damage()
        dps = total_damage / rotation_time

        if dps > best_dps:
            best_dps = dps
            best_profile = profile

    constellations = team_config["constellations"]

    if best_profile is not None:
        (
            atk_rolls,
            atk_percent_rolls,
            cd_rolls,
            em_rolls,
            cr_rolls,
            er_rolls,
        ) = best_profile

        base_crit_rate = (
            24.2
            + cr_rolls * ARTIFACT_SUBSTATS["CR%"]["average"]
        )

        if (
            "diona" in team_config["members"]
            and "odette" in team_config["members"]
        ):
            crit_rate = min(100.0, base_crit_rate + 30.8)
        else:
            crit_rate = min(85.0, base_crit_rate + 15.8)

        best_vesna = VesnaTeamDPSTheory(
            flat_attack_value=atk_rolls * roll_averages["ATK"],
            atk_percent=(atk_percent_rolls* ARTIFACT_SUBSTATS["ATK%"]["average"]),
            crit_damage=(cd_rolls* ARTIFACT_SUBSTATS["CD%"]["average"]),
            elemental_mastery=em_rolls * roll_averages["EM"],
            crit_rate=crit_rate / 100.0,
            energy_recharge=(er_rolls * ARTIFACT_SUBSTATS["ER%"]["average"]),
            team_name=team_config["team_name"],
            current_configuration=team_config.copy(),
        )
        rotation_time = best_vesna.rotation_duration
        members = set(team_config["members"])
        # Vesna damage
        vesna_rotation_damage = (best_vesna.calculate_total_vesna_damage())
        vesna_dps = vesna_rotation_damage / rotation_time

        # Odette - Stellar damage
        odette_on_field_stellar = (best_vesna.odette_on_field_Coda_stellar_swirl_damage+ best_vesna.odette_on_field_C1_additional_stellar_damage)

        # Odette - On-Field Cryo damage
        odette_on_field_cryo = best_vesna.odette_on_field_cryo_damage

        # Odette Total on-field damage
        odette_on_field_total = (odette_on_field_stellar+ odette_on_field_cryo)

        odette_off_field_stellar = (
            best_vesna.odette_off_field_Coda_stellar_swirl_damage
            + best_vesna.odette_plume_stellar_hits
            * best_vesna.odette_off_field_plume_stellar_swirl_damage
            + best_vesna.odette_wing_stellar_hits
            * best_vesna.odette_off_field_wing_stellar_swirl_damage
        )

        # Lumine Damage Breakdown
        lumine_stellar_charge_attack = (best_vesna.lumine_stellar_charge_attack_damage if "lumine" in members else 0.0)
        lumine_e_skill_on_field = (best_vesna.lumine_e_skill_cryo_damage_on_field if "lumine" in members else 0.0)
        lumine_e_skill_off_field = (best_vesna.lumine_e_skill_cryo_damage_off_field if "lumine" in members else 0.0)
        lumine_ultimate_q = (best_vesna.lumine_ultimate_q_stellar_damage if "lumine" in members else 0.0)

        # Lumine - Cryo and Stellar damage
        lumine_rotation_damage = (lumine_stellar_charge_attack+ lumine_e_skill_on_field+ lumine_e_skill_off_field+ lumine_ultimate_q)
        # Anastasya Damage Breakdown
        anastasya_e_skill_cryo_damage_on_field = (best_vesna.anastasya_e_skill_cryo_damage_on_field if "anastasya" in members else 0.0)
        anastasya_e_skill_cryo_damage_off_field = (best_vesna.anastasya_e_skill_cryo_damage_off_field if "anastasya" in members else 0.0)
        anastasya_e_skill_stellar_damage_off_field = (best_vesna.anastasya_e_skill_stellar_damage_off_field if "anastasya" in members else 0.0)
        anastasya_ultimate_q_stellar_damage = (best_vesna.anastasya_ultimate_q_stellar_damage if "anastasya" in members else 0.0)
        anastasya_ultimate_q_stellar_damage_off_field_tick_damage = (best_vesna.anastasya_ultimate_q_stellar_damage_off_field_tick_damage if "anastasya" in members else 0.0)
        anastasya_ultimate_q_cryo_damage_on_field =(best_vesna.anastasya_ultimate_q_cryo_damage_on_field if "anastasya" in members else 0.0)

        anastasya_rotation_damage = (
            anastasya_e_skill_cryo_damage_on_field
            + anastasya_e_skill_cryo_damage_off_field
            + anastasya_e_skill_stellar_damage_off_field
            + anastasya_ultimate_q_stellar_damage
            + anastasya_ultimate_q_stellar_damage_off_field_tick_damage
            + anastasya_ultimate_q_cryo_damage_on_field
        )

        anastasya_dps = anastasya_rotation_damage / rotation_time

        # DEBUG: Artifact set assignments
        artifact_buffs = best_vesna.active_team_artifact_set_distribution_and_buffs

        odette_rotation_damage = (odette_on_field_total+ odette_off_field_stellar + best_vesna.vortex_procs * best_vesna.calculate_odette_vortex_proc_damage(level=90) + best_vesna.vortex_explosions * best_vesna.calculate_odette_vortex_explosion_damage(level=90))
        odette_dps = odette_rotation_damage / rotation_time
        lumine_dps = lumine_rotation_damage / rotation_time

        # DPS contributions from other team members
        diona_dps_value = 5000.0 if "diona" in members else 0.0
        faruzan_dps_value = 15000.0 if "faruzan" in members else 0.0
        sucrose_dps_value = 2500.0 if "sucrose" in members else 0.0
        vodyanitsa_flat_dps = 750.0 if "vodyanitsa" in members else 0.0


        # Individual dps shown
        vesna_dps = vesna_dps if "vesna" in members else 0.0
        odette_dps = odette_dps if "odette" in members else 0.0
        lumine_dps = lumine_dps if "lumine" in members else 0.0
        anastasya_dps = anastasya_dps if "anastasya" in members else 0.0

        # Individual damage shown
        vesna_rotation_damage = vesna_rotation_damage if "vesna" in members else 0.0
        odette_rotation_damage = odette_rotation_damage if "odette" in members else 0.0
        lumine_rotation_damage = lumine_rotation_damage if "lumine" in members else 0.0
        anastasya_rotation_damage = anastasya_rotation_damage if "anastasya" in members else 0.0

        team_dps = (
            vesna_dps
            + odette_dps
            + diona_dps_value
            + faruzan_dps_value
            + sucrose_dps_value
            + vodyanitsa_flat_dps
            + lumine_dps
            + anastasya_dps
        )
        team_rotation_damage = team_dps * rotation_time
    
        # Final report
        print("TEAM OVERVIEW")
        print(f"Team: {team_config['team_name']}")
        print()
        print("-" * 60)
        print("CHARACTER CONSTELLATIONS")
        print("-" * 60)
        print(f"Vesna: C{int(constellations.get('vesna', 0))}")
        print(f"Odette: C{int(constellations.get('odette', 0))}")
        print(f"Anastasya: C{int(constellations.get('anastasya', 0))}")
        print(f"Vodyanitsa: C{int(constellations.get('vodyanitsa', 0))}")

        print()
        print("-" * 60)
        print("ARTIFACT SET ASSIGNMENTS")
        print("-" * 60)

        for set_name, details in artifact_buffs.items():
            holder = details.get("holder")
            print(f"{set_name}: {holder if holder is not None else 'no holder'}")

        print()
        print("-" * 60)
        print("BEST ARTIFACT PROFILE")
        print("-" * 60)
        print(f"(ATK, ATK%, CD%, EM, CR%, ER%): {best_profile}")

        print()
        print("-" * 60)
        print("CHARACTER DAMAGE BREAKDOWN")
        print("-" * 60)
        print(f"Vesna Rotation Damage:      {vesna_rotation_damage:,.2f}")
        print(f"Vesna DPS:                  {vesna_dps:,.2f}")
        print()
        print(f"Odette Rotation Damage:     {odette_rotation_damage:,.2f}")
        print(f"Odette DPS:                 {odette_dps:,.2f}")
        print()
        print(f"Lumine Rotation Damage:     {lumine_rotation_damage:,.2f}")
        print(f"Lumine DPS:                 {lumine_dps:,.2f}")
        print()
        print(f"Anastasya Rotation Damage:  {anastasya_rotation_damage:,.2f}")
        print(f"Anastasya DPS:              {anastasya_dps:,.2f}")
        print()
        print(f"Diona DPS:                  {diona_dps_value:,.2f}")
        print(f"Faruzan DPS:                {faruzan_dps_value:,.2f}")
        print(f"Sucrose DPS:                {sucrose_dps_value:,.2f}")
        print(f"Vodyanitsa DPS:             {vodyanitsa_flat_dps:,.2f}")

        print()
        print("-" * 60)
        print("TEAM DAMAGE")
        print("-" * 60)
        print(f"Rotation Duration:          {rotation_time:.2f} s")
        print(f"Total Team Rotation Damage: {team_rotation_damage:,.2f}")
        print(f"TOTAL TEAM DPS:             {team_dps:,.2f}")
        print("=" * 60)
        # Export data
        export_data = VesnaDPSTheoryExport(
            configuration=configuration,
            team_name=team_config["team_name"],
            configuration_name=team_config.get("configuration_name", ""),
            line_type=line_type,

            vesna_constellation=int(constellations.get("vesna", 0)),
            anastasya_constellation=int(constellations.get("anastasya", 0)),
            odette_constellation=int(constellations.get("odette", 0)),
            vodyanitsa_constellation=int(constellations.get("vodyanitsa", 0)),


            artifact_sets={
                set_name: details.get("holder")
                for set_name, details in artifact_buffs.items()
            },

            best_profile=best_profile,

            vesna_rotation_damage=vesna_rotation_damage,
            vesna_dps=vesna_dps,

            odette_rotation_damage=odette_rotation_damage,
            odette_dps=odette_dps,

            lumine_dps=lumine_dps,
            diona_dps=diona_dps_value,
            faruzan_dps=faruzan_dps_value,
            sucrose_dps=sucrose_dps_value,
            vodyanitsa_dps=vodyanitsa_flat_dps,

            rotation_duration=rotation_time,
            team_rotation_damage=team_rotation_damage,
            team_dps=team_dps,
        )
    return best_profile, best_dps, export_data if best_profile is not None else None

# 13. PROGRAM ENTRY POINT – OUTSIDE THE CLASS
if __name__ == "__main__":
    log_path = Path(__file__).with_name("vesna_calc.log")
    log_file = log_path.open("w", encoding="utf-8")

    sys.stdout = Tee(sys.stdout, log_file)

    calculator = VesnaTeamDPSTheory()
    line_type = "3_line"
    combined_profiles = load_or_calculate_profiles(line_type)

    total_configurations = len(calculator.all_team_configurations)

    export_results: list[VesnaDPSTheoryExport] = []

    for index, config in enumerate(
        calculator.all_team_configurations,
        start=1,
    ):
        print(
            f"\n{'=' * 60}\n"
            f"Configuration {index}/{total_configurations}"
        )

        best_profile, best_dps, export_data = find_best_dps_profile(
            combined_profiles,
            line_type,
            config,
            configuration=index,
        )
        if export_data is not None: export_results.append(export_data)

    VesnaDPSTheoryExport.export_to_excel(
        export_results,
        output_path=Path(__file__).with_name("vesna_team_with_anastasya_dps.xlsx"), #here change the name of the file
    )

    print("\nExcel export completed.")
    sys.stdout = sys.__stdout__
    log_file.close()
