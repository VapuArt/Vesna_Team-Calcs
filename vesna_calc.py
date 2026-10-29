from ast import Set
from dataclasses import dataclass, field
from encodings import raw_unicode_escape
from itertools import product, combinations
import json
from os import listvolumes
from pathlib import Path
from typing import ClassVar
import sys
import atexit
from xml.sax.handler import property_declaration_handler
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
class VesnaTeamDPSTheorie:
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


    def calculate_anemo_res_multiplier(self) -> float:
        effective_resistance = (
            self.enemy_anemo_resistance
            - self.vesna_anemo_res_reduction
        ) / 100.0

        if effective_resistance < 0.0:
            return 1.0 - effective_resistance / 2.0

        if effective_resistance < 0.75:
            return 1.0 - effective_resistance

        return 1.0 / (4.0 * effective_resistance + 1.0)

    def calculate_cryo_res_multiplier(self) -> float:
        effective_resistance = (
            self.enemy_cryo_resistance
            - self.odette_cryo_res_reduction
        ) / 100.0

        if effective_resistance < 0.0:
            return 1.0 - effective_resistance / 2.0

        if effective_resistance < 0.75:
            return 1.0 - effective_resistance

        return 1.0 / (4.0 * effective_resistance + 1.0)

    @property
    def team_wide_stellar_damage_bonus(self) -> float:
        """Returns the combined team-wide Stellar damage bonus in percent."""

        buff = 0.0

        # Odette: Marvelous Splendor stacks and Furnace set bonus
        if self.is_odette_active:
            stacks = (
                self.odette_C1_marvelous_splender_stacks
                if self.odette_constellation >= 1
                else self.odette_marvelous_splender_stacks
            )
            buff += self.odette_C0_stellar_damage * stacks
            buff += self.odette_furnace_set_stellar_damage_bonus

        # Faruzan's Breezeborne R5 bonus, if Diona or Faruzan is active
        if self.is_diona_active or self.is_faruzan_active:
            buff += self.faruzan_breezeborne_r5_stellar_damage_bonus

        # Diona: C6 Stellar damage bonus
        if self.is_diona_active:
            buff += self.diona_C6_stellar_damage_bonus

        # Lumine C6: up to +40% Stellar Glimmer reaction damage for 15s
        if self.is_lumine_active:
            buff += 40.0

        return buff

    @property
    def active_team_artifact_buffs(self) -> dict:
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

        # ToM priority: Vodyanitsa > Diona
        if self.is_vodyanitsa_active:
            tom_holder = "vodyanitsa"
        elif self.is_diona_active:
            tom_holder = "diona"
        else:
            tom_holder = None

        # Noblesse holder: Diona only when Vodyanitsa is in the team.
        # Vesna recieves Nobless buff by switching onto the field immediately after the Noblesse holder.
        if self.is_diona_active and self.is_vodyanitsa_active:
            noblesse_holder = "diona"
        else:
            noblesse_holder = None

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

        buffs["lumine_2p2p_atk"] = {
            "holder": "lumine" if self.is_lumine_active and furnace_holder != "lumine" else None,
            "atk_bonus": 36.0,
        }

        # --------------------------------------------------
        # 7. Instructor
        # --------------------------------------------------

        buffs["instructor"] = {
            "holder": "sucrose" if furnace_holder != "sucrose" else None,
            "uptime": 0.8 if self.is_odette_active and furnace_holder != "sucrose" else 0.0,
            "rotation_duration": 20.0 if self.is_odette_active and furnace_holder != "sucrose" else None,
            "conditions": {
                # The rotation switches to Sucrose twice before Odette and Vesna.
                "odette_and_vesna_uptime_80_percent": True,
            },
        }

        return buffs

    @property
    def active_team_stellar_buffs(self) -> dict:
        """Returns Stellar buffs currently active in the team rotation."""
        buffs = {}

        # Add each buff only when its rotation conditions are met.
        # Store its value, duration and eligible recipients.

        return buffs
    # 2. VESNA – character stats and MV
    vesna_level_90: int = 90
    vesna_level_95: int = 95
    level: int = 95
    base_atk_lv_90: float = 1028
    base_atk_lv_95: float = 1068
    vesna_flat_atk_feather: float = 311
    vesna_base_em: float = 0.0
    atk_percent_vesna_a3_solo: float = 6

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

    vesna_talent_stellar_damage_bonus: float = 14
    stellar_quills_flat_damage_without_vodya: float = 0

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

    # Team-Buffs
    atk_percent_vesna_a3_value_odette: float = 6.0


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
    odette_furnace_set_stellar_damage_bonus: float = 50.0


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
    def active_odette_talent_stellar_damage_bonus(self) -> float:
        if self.is_odette_active:
            return self.odette_talent_stellar_damage_bonus
        return 0.0

    @property
    def odette_total_stellar_damage_bonus(self) -> float:
        stacks = self.odette_marvelous_splender_stacks

        # Odette C1 – Marvelous Splendor uses 6 stacks.
        if self.current_configuration["constellations"].get("odette", 0) >= 1:
            stacks = self.odette_C1_marvelous_splender_stacks

        bonus = (
            self.odette_C0_stellar_damage * stacks
            + self.odette_personal_stellar_damage_bonus
            + self.odette_furnace_set_stellar_damage_bonus
        )

        # Faruzan's / Diona's Breezeborne R5 bonus
        # Diona Q EM / Stellar Buff is not active here
        if self.is_diona_active or self.is_faruzan_active:
            bonus += self.faruzan_breezeborne_r5_stellar_damage_bonus

        return bonus

    @property
    def odette_off_field_stellar_damage_bonus(self) -> float:
        return self.odette_furnace_set_stellar_damage_bonus
    @property
    def odette_atk_percent_value(self) -> float:
        return self.team_atk_percent_buff
    @property
    def odette_on_field_atk(self) -> float:
        return (
            self.odette_atk
            + self.odette_base_atk
            * self.odette_atk_percent_value
            / 100.0
            
        )
    @property
    def odette_off_field_atk(self) -> float:
        return self.odette_atk
    @property
    def odette_stellar_swirl_crit_multiplier(self) -> float:
        effective_cr = self.odette_cr

        # Cryo Resonance: +15% Crit Rate when Odette and Diona are on the team.
        if (
            "diona" in self.current_configuration["members"]
            and "odette" in self.current_configuration["members"]
        ):
            effective_cr += 15.0

        effective_cr = min(effective_cr, 100.0)

        # Vodyanitsa C2: zusätzlicher Stellar-Swirl-Crit-Schaden
        crit_damage = (
            self.odette_cd
            + self.vodyanitsa_stellar_swirl_crit_damage_bonus
        )

        return 1 + effective_cr / 100.0 * crit_damage / 100.0
    @property
    def odette_cryo_crit_multiplier(self) -> float:
        effective_cr = self.odette_cr

        # Cryo Resonance: +15% Crit Rate when Odette and Diona are on the team.
        if (
            "diona" in self.current_configuration["members"]
            and "odette" in self.current_configuration["members"]
        ):
            effective_cr += 15.0

        effective_cr = min(effective_cr, 100.0)

        return 1 + effective_cr / 100.0 * self.odette_cd / 100.0
    @property
    def odette_off_field_stellar_swirl_crit_multiplier(self) -> float:
        effective_cr = self.odette_cr

        # Cryo Resonance: +15% Crit Rate when Odette and Diona are on the team.
        if ("diona" in self.current_configuration["members"] and "odette" in self.current_configuration["members"]):
            effective_cr += 15.0

        effective_cr = min(effective_cr, 100.0)
        crit_damage = (self.odette_cd + self.vodyanitsa_stellar_swirl_crit_damage_bonus)

        return 1 + effective_cr / 100.0 * crit_damage / 100.0
    @property
    def odette_off_field_cryo_crit_multiplier(self) -> float:
        effective_cr = self.odette_cr

        # Cryo Resonance: +15% Crit Rate when Odette and Diona are on the team.
        if (
            "diona" in self.current_configuration["members"]
            and "odette" in self.current_configuration["members"]
        ):
            effective_cr += 15.0

        effective_cr = min(effective_cr, 100.0)

        return 1 + effective_cr / 100.0 * self.odette_cd / 100.0
    @property
    def odette_em_multiplier(self) -> float:
        em = (self.odette_em + (self.lumine_frostfall_reverberation_em_bonus if self.is_lumine_active else 0))

        # Stellar base bonus: Odette 14% + Vesna 14% + 7% Lumine
        talent_stellar_bonus = (self.odette_talent_stellar_damage_bonus+ self.vesna_talent_stellar_damage_bonus) + (self.lumine_stellar_jubilee_talent_stellar_base_damage_mod / 100 if self.is_lumine_active else 0)
        em_and_stellar_multiplier = (1+ 6 * em / (2000 + em)+ self.odette_total_stellar_damage_bonus / 100.0)
        return (1 + talent_stellar_bonus / 100.0) * em_and_stellar_multiplier

    @property
    def odette_off_field_em_multiplier(self) -> float:
        em = self.odette_em

        # Stellar base bonus: Odette 14% + Vesna 14% + 7% Lumine
        talent_stellar_bonus = (self.odette_talent_stellar_damage_bonus+ self.vesna_talent_stellar_damage_bonus) + (self.lumine_stellar_jubilee_talent_stellar_base_damage_mod / 100 if self.is_lumine_active else 0)

        # The EM contribution and Stellar damage bonus are added together.
        em_and_stellar_multiplier = (1+ 6 * em / (2000 + em)+ self.odette_off_field_stellar_damage_bonus / 100.0)

        return (1 + talent_stellar_bonus / 100.0) * em_and_stellar_multiplier
    @property
    def odette_cryo_res_reduction(self) -> float:
        reduction = 0.0

        if self.is_vodyanitsa_active: 
            reduction += self.vodyanitsa_cryo_res_reduction

        if (self.is_odette_active and self.current_configuration["constellations"].get("odette", 0) >= 2):
            reduction += self.odette_C2_cryo_res_reduction

        if self.is_faruzan_active:
            reduction += self.faruzan_VV_set_cryo_res_reduction

        return reduction


    # 4. VODYANITSA – CHARACTER STATS
    # we are running on Vodyanitsa always her Signature weapon and 2p/2p HP to reach the 65k HP threshhold
    # not running ToM will result in slightly lower numbers, but there is less headache about calculating uptimes for different artifact set combinations in different teams
    # this whole stuff might be added in the future
    vodyanitsa_HP_value: float = 65000.0
    vodyanitsa_stellar_quills_flat_damage: float = 6500.0
    vodyanitsa_flat_dps: float = 750.0
    em_vesna_talent_a3_vodyanitsa: float = 25

    vodyanitsa_anemo_res_reduction: float = 35.0
    vodyanitsa_cryo_res_reduction: float = 30.0
    vodyanitsa_signature_atk_bonus: float = 42.0
    vodyanitsa_C1_additional_atk: float = 520.0
    vodyanitsa_C2_stellar_reaction_cd_bonus: float = 60.0

    @property
    def vodyanitsa_stellar_swirl_crit_damage_bonus(self) -> float:
        if (
            self.is_vodyanitsa_active
            and self.current_configuration["constellations"].get("vodyanitsa", 0) >= 2
        ):
            return self.vodyanitsa_C2_stellar_reaction_cd_bonus
        return 0.0

    @property
    def active_vodyanitsa_stellar_quills_flat_damage(self) -> float:
        if self.is_vodyanitsa_active:
            return self.vodyanitsa_stellar_quills_flat_damage
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
    faruzan_breezeborne_r5_stellar_damage_bonus: float = 48.0


    # 7. SUCROSE – C6
    atk_percent_vesna_a3_value_sucrose: float = 6
    sucrose_total_em_value: float = 860.0
    sucrose_dps_value: float = 2500.0

    sucrose_instrcutor_em_value: float = 120.0
    sucrose_talent_catalyst_conversion_em_value: float = 50.0
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
    lumine_sig_base_cr_value: float = 33.1
    lumine_sig_CD_value: float = 42
    lumine_sig_atk_value: float = 40
    
    lumine_pyro_talent_atk_bonus: float = 20
    lumine_base_em_value: float = 280 #160 from talent + 60 from dendro + 60 from 100% uptime E Skill
    lumine_ascension_stat_atk_percent: float = 24

    #Stats from artifacts
    lumine_2p2p_atk_artifact_set_bonus: float = 36.0
    lumine_feather_flat_atk_bonus: float = 311
    lumine_base_atk_total: float = lumine_base_atk + lumine_sig_base_atk
    lumine_artifact_sands_atk_value:float = 46.6
    lumine_artifact_goblet_atk_value:float = 46.6
    lumine_artifact_circlet_cd_value:float = 62.2

    lumine_total_CR: float = 85.0
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
    def lumine_total_CR(self) -> float:
        cr = 85.0

        if self.is_odette_active or self.is_diona_active:
            cr += 15.0

        return min(cr, 100.0)
    @property
    def lumine_crit_multiplier(self) -> float:
        return 1.0 + (
            self.lumine_total_CR / 100.0
        ) * (
            self.lumine_total_CD / 100.0
        )

    @property
    def lumine_base_atk_total(self) -> float:
        return self.lumine_base_atk + self.lumine_sig_base_atk
     
    @property
    def lumine_total_atk(self) -> float:
        return (
            self.lumine_base_atk_total
            * (
                1
                + (
                    self.lumine_sig_atk_value
                    + self.lumine_ascension_stat_atk_percent
                    + self.lumine_2p2p_atk_artifact_set_bonus
                    + self.lumine_pyro_talent_atk_bonus
                    + self.lumine_artifact_sands_atk_value
                    + self.lumine_artifact_goblet_atk_value
                ) / 100
            )
            + self.lumine_feather_flat_atk_bonus
        )
    @property
    def lumine_on_field_total_atk_value(self) -> float:
        return (
            self.lumine_total_atk 
            + (self.lumine_base_atk_total * self.team_atk_percent_buff / 100) 
            )

    @property
    def lumine_stellar_base_dmg_team_damage_bonus(self) -> float:
        bonus = self.vesna_talent_stellar_damage_bonus + self.lumine_stellar_jubilee_talent_stellar_base_damage_mod
        if self.is_odette_active:
            bonus += 14
        if self.is_anastasya_active: #need to wait for confirmation
            bonus += 14
        return bonus

    @property
    def lumine_em_multiplier(self) -> float:
        return (1+ 6*self.lumine_total_em /(self.lumine_total_em+2000))*(1+ self.lumine_stellar_base_dmg_team_damage_bonus / 100) + (1+self.lumine_total_stellar_damage_percent_bonus/100)
    
    @property
    def lumine_total_stellar_damage_percent_bonus(self) -> float:
        bonus = 0.0

        if self.is_odette_active:
            if self.current_configuration["constellations"].get("odette", 0) >= 1:
                stacks = self.odette_C1_marvelous_splender_stacks
            else:
                stacks = self.odette_marvelous_splender_stacks

            bonus += stacks * self.odette_C0_stellar_damage
            bonus += self.odette_furnace_set_stellar_damage_bonus

        #if (self.is_diona_active and self.current_configuration["constellations"].get("diona", 0) >= 6):
        #   bonus += self.diona_C6_stellar_damage_bonus

        if self.is_diona_active or self.is_faruzan_active:
            bonus += self.faruzan_breezeborne_r5_stellar_damage_bonus

        return bonus

    @property
    def lumine_stellar_charge_attack_damage(self) -> float:
        damage = (self.lumine_on_field_total_atk_value * (self.lumine_mv_stellar_CA_mv_with_talent / 100.0) * self.lumine_em_multiplier)

        return (damage * self.lumine_crit_multiplier * self.calculate_cryo_res_multiplier())

    @property
    def lumine_e_skill_cryo_damage_on_field(self) -> float:
        damage = (
            self.lumine_on_field_total_atk_value
            * (self.lumine_mv_E_Skill_On_field_inital_mv_value / 100.0)
        )

        return (
            damage
            * self.lumine_crit_multiplier
            * self.general_defense_multiplier_90
            * self.calculate_cryo_res_multiplier()
        )

    @property
    def lumine_e_skill_cryo_damage_off_field(self) -> float:
        damage_per_tick = (
            self.lumine_total_atk
            * (self.lumine_mv_E_Skill_off_field_periodic_mv_value / 100.0)
        )

        return (
            damage_per_tick
            * self.lumine_mv_E_Skill_off_fiel_periodic_tick_amount
            * self.lumine_crit_multiplier
            * self.general_defense_multiplier_90
            * self.calculate_cryo_res_multiplier()
        )

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
            self.lumine_on_field_total_atk_value
            * (total_mv / 100.0)
            * self.lumine_em_multiplier
            * (1 + frostglow_bonus / 100.0)
        )

        return (
            damage
            * self.lumine_crit_multiplier
            * self.calculate_cryo_res_multiplier()
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

    @property
    def lumine_rotation_dps(self) -> float:
        """Average DPS of Lumine over a 19.5-second rotation."""
        return self.lumine_rotation_damage / 19.5

    # 8. Team Comps and definitions
    TEAMS: ClassVar[list[dict]] = [
        {"name": "Vesna_Odette_Vodyanitsa_Faruzan",
         "members": ["vesna", "odette", "vodyanitsa", "faruzan"]},

        {"name": "Vesna_Odette_Vodyanitsa_Diona",
         "members": ["vesna", "odette", "vodyanitsa", "diona"]},

        {"name": "Vesna_Odette_Vodyanitsa_Sucrose",
         "members": ["vesna", "odette", "vodyanitsa", "sucrose"]},

        {"name": "Vesna_Odette_Faruzan_Diona",
         "members": ["vesna", "odette", "faruzan", "diona"]},

        {"name": "Vesna_Odette_Faruzan_Sucrose",
         "members": ["vesna", "odette", "faruzan", "sucrose"]},

        {"name": "Vesna_Vodyanitsa_Faruzan_Diona",
         "members": ["vesna", "vodyanitsa", "faruzan", "diona"]},

        {"name": "Vesna_Vodyanitsa_Faruzan_Sucrose",
         "members": ["vesna", "vodyanitsa", "faruzan", "sucrose"]},

        {"name": "Vesna_Odette_Diona_Sucrose",
         "members": ["vesna", "odette", "diona", "sucrose"]},

        {"name": "Vesna_Vodyanitsa_Diona_Sucrose",
         "members": ["vesna", "vodyanitsa", "diona", "sucrose"]},

        {"name": "Vesna_Faruzan_Diona_Sucrose",
         "members": ["vesna", "faruzan", "diona", "sucrose"]},

        {"name": "Vesna_Odette_Vodyanitsa_Lumine",
         "members": ["vesna", "odette", "vodyanitsa", "lumine"]},

        {"name": "Vesna_Odette_Faruzan_Lumine",
         "members": ["vesna", "odette", "faruzan", "lumine"]},

        {"name": "Vesna_Odette_Diona_Lumine",
         "members": ["vesna", "odette", "diona", "lumine"]},

        {"name": "Vesna_Odette_Sucrose_Lumine",
         "members": ["vesna", "odette", "sucrose", "lumine"]},

        {"name": "Vesna_Vodyanitsa_Faruzan_Lumine",
         "members": ["vesna", "vodyanitsa", "faruzan", "lumine"]},

        {"name": "Vesna_Vodyanitsa_Diona_Lumine",
         "members": ["vesna", "vodyanitsa", "diona", "lumine"]},

        {"name": "Vesna_Vodyanitsa_Sucrose_Lumine",
         "members": ["vesna", "vodyanitsa", "sucrose", "lumine"]},

        {"name": "Vesna_Faruzan_Diona_Lumine",
         "members": ["vesna", "faruzan", "diona", "lumine"]},

        {"name": "Vesna_Faruzan_Sucrose_Lumine",
         "members": ["vesna", "faruzan", "sucrose", "lumine"]},

        {"name": "Vesna_Diona_Sucrose_Lumine",
         "members": ["vesna", "diona", "sucrose", "lumine"]},
    ]

    VESNA_CONSTELLATIONS: ClassVar[list[float]] = [0.0, 1.0, 2.0]
    ODETTE_CONSTELLATIONS: ClassVar[list[float]] = [0.0, 1.0, 2.0]
    VODYANITSA_CONSTELLATIONS: ClassVar[list[float]] = [0.0, 1.0, 2.0]

    team_name: str = "Vesna_Odette_Vodyanitsa_Faruzan"
    current_configuration: dict = field(default_factory=dict)

    # 9. VESNA – STATS AND DAMAGE MULTIPLIERS
    def print_vesna_damage_breakdown(self) -> None:
        """Displays Vesna's stats, damage bonuses, and damage breakdown."""

        def section(title):
            print(f"\n{'=' * 18} {title} {'=' * 18}")

        def show(label, value):
            print(f"{label:<42} {value}")

        section("TEAM")
        show("Active team members", self.active_team_members)
        show("Odette active", self.is_odette_active)
        show("Faruzan active", self.is_faruzan_active)
        show("Diona active", self.is_diona_active)

        section("ATK")
        show("Base ATK", self.vesna_base_atk_value)
        show("ATK% bonus", self.vesna_atk_percent_value)
        show("Team ATK% bonus", self.team_atk_percent_buff)
        show("Flat ATK from Feather", self.vesna_flat_atk_feather)
        show("Other flat ATK", self.flat_attack_value)
        show("Team flat ATK", self.team_atk_flat_buff)
        show("Total ATK", self.vesna_total_atk_value)

        section("STELLAR DAMAGE")
        show("Artifact bonus", self.vesna_artifact_set_stellar_bonus)
        show("Weapon bonus", self.vesna_weapon_stellar_bonus)
        show("Team bonus", self.team_stellar_damage_bonus_vesna)
        show("Total Stellar damage bonus (%)", self.vesna_total_stellar_bonus)
        show("Elemental Mastery", self.vesna_em_value)
        show("Stellar damage multiplier", self.stellar_damage_multiplier)

        section("CRIT")
        show("Crit Rate (%)", self.crit_rate * 100)
        show("Crit DMG (%)", self.vesna_crit_damage_value)
        show("Stellar Crit multiplier", self.stellar_crit_multiplier)
        show("Anemo Crit multiplier", self.anemo_crit_multiplier)
        show("Vodyanitsa Stellar Swirl Crit DMG bonus",self.vodyanitsa_stellar_swirl_crit_damage_bonus)

        section("RESISTANCE REDUCTION")
        show("Faruzan active", self.is_faruzan_active)
        show("Vodyanitsa active", self.is_vodyanitsa_active)
        show("Odette active", self.is_odette_active)
        show("Anemo RES reduction – Faruzan", self.faruzan_anemo_res_reduction)
        show("Anemo RES reduction – Vodyanitsa", self.vodyanitsa_anemo_res_reduction)
        show("Anemo RES reduction – Odette C2", self.odette_C2_anemo_res_reduction)
        show("Total Anemo RES reduction", self.vesna_anemo_res_reduction)
        show("Cryo RES reduction – Vodyanitsa", self.vodyanitsa_cryo_res_reduction)
        show("Cryo RES reduction – Odette C2", self.odette_C2_cryo_res_reduction)
        show("Cryo RES reduction – Faruzan VV", self.faruzan_VV_set_cryo_res_reduction)
        show("Total Cryo RES reduction", self.vesna_cryo_res_reduction)
        show("Anemo RES multiplier (10% base RES)",self.calculate_res_multiplier(10.0, self.vesna_anemo_res_reduction),)
        show("Cryo RES multiplier (10% base RES)",self.calculate_res_multiplier(10.0, self.vesna_cryo_res_reduction),)

        section("DAMAGE BREAKDOWN")
        show("Anemo damage", self.calculate_anemo_damage_lv95())
        show("Stellar damage", self.vesna_total_stellar_damage)
        show("Vortex damage", self.calculate_vesna_total_vortex_damage(95))
        show("Total damage", self.calculate_total_vesna_damage())

        section("END")

        level = 95

        if level == 90:
            level_modifier = self.lv90_modifier
        elif level == 95:
            level_modifier = self.lv95_modifier
        else:
            raise ValueError(f"Unsupported enemy level: {level}")

        vortex_proc_base = level_modifier * 0.75 * 0.6
        vortex_explosion_base = level_modifier * 3.0 * 0.6

        vortex_damage_bonus = (
            1.0 + (self.vesna_talent_stellar_damage_bonus+ self.active_odette_talent_stellar_damage_bonus) / 100.0)

        vortex_res_multiplier = self.calculate_res_multiplier(
            10.0,
            self.vesna_cryo_res_reduction,
        )

        section("ODETTE – DAMAGE BREAKDOWN")

        show("Level", self.odette_lv)
        show("On-Field ATK", self.odette_on_field_atk)
        show("Off-Field ATK", self.odette_off_field_atk)
        show("Elemental Mastery", self.odette_em)
        show("Crit Rate (%)", self.odette_cr)
        show("Crit DMG (%)", self.odette_cd)

        # Damage Bonuses
        show("On-Field Stellar DMG Bonus (%)", self.odette_total_stellar_damage_bonus)
        show("Off-Field Stellar DMG Bonus (%)", self.odette_off_field_stellar_damage_bonus)
        show("Talent Stellar DMG Bonus (%)", self.active_odette_talent_stellar_damage_bonus)
        show("Cryo RES Reduction (%)", self.odette_cryo_res_reduction)

        # E Damage
        show("Coda Stellar Swirl (On-Field)", self.odette_on_field_Coda_stellar_swirl_damage)
        show("Plume Stellar Swirl (On-Field, per hit)", self.odette_on_field_plume_stellar_swirl_damage)
        show("Wing Stellar Swirl (On-Field, per hit)", self.odette_on_field_wing_stellar_swirl_damage)

        show("Coda Stellar Swirl (Off-Field)", self.odette_off_field_Coda_stellar_swirl_damage)
        show("Plume Stellar Swirl (Off-Field, per hit)", self.odette_off_field_plume_stellar_swirl_damage)
        show("Wing Stellar Swirl (Off-Field, per hit)", self.odette_off_field_wing_stellar_swirl_damage)

        section("END")

    @property
    def vesna_atk_percent_value(self) -> float:
        return (
            self.atk_percent_sands
            + self.atk_percent_goblet
            + self.atk_percent_set_bonus
            + self.atk_percent_vesna_a3_solo
            + self.atk_percent
        )

    @property
    def vesna_base_atk_value(self) -> float:
        if self.level == self.vesna_level_90:
            return self.base_atk_lv_90
        elif self.level == self.vesna_level_95:
            return self.base_atk_lv_95
        raise ValueError(f"Unsupported Vesna level: {self.level}")

    @property
    def vesna_total_atk_value(self) -> float:
        total_atk_percent = (
            self.vesna_atk_percent_value
            + self.team_atk_percent_buff
        )

        return (
            self.vesna_base_atk_value
            * (1.0 + total_atk_percent / 100.0)
            + self.vesna_flat_atk_feather
            + self.flat_attack_value
            + self.team_atk_flat_buff
        )

    @property
    def vesna_em_value(self) -> float:
        return (
            self.vesna_base_em
            + self.elemental_mastery
            + self.team_em_buff_vesna
            + (self.lumine_frostfall_reverberation_em_bonus_after_stellar_damage if self.is_lumine_active
                else 0
            )
        )

    @property
    def vesna_total_stellar_bonus(self) -> float:
        return (
            self.vesna_artifact_set_stellar_bonus
            + self.vesna_weapon_stellar_bonus
            + self.team_stellar_damage_bonus_vesna
        )

    @property
    def stellar_damage_multiplier(self) -> float:
        return (
            1.0
            + (6.0 * self.vesna_em_value)
            / (self.vesna_em_value + 2000.0)
            + self.vesna_total_stellar_bonus / 100.0
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
    def stellar_crit_multiplier(self) -> float:
        crit_damage = (
            self.vesna_crit_damage_value
            + self.vodyanitsa_stellar_swirl_crit_damage_bonus
        )

        if (
            self.is_faruzan_active
            and self.current_configuration["constellations"].get("faruzan", 0) >= 6
        ):
            crit_damage += self.faruzan_c6_anemo_crit_damage

        return 1.0 + crit_damage / 100.0

    @property
    def anemo_crit_multiplier(self) -> float:
        crit_damage = self.vesna_crit_damage_value

        if (
            self.is_faruzan_active
            and self.current_configuration["constellations"].get("faruzan", 0) >= 6
        ):
            crit_damage += self.faruzan_c6_anemo_crit_damage

        return 1.0 + crit_damage / 100.0



    # 10. VESNA – DAMAGE CALCULATIONS
    def calculate_anemo_damage_lv90(self) -> float:
        return (
            self.vesna_total_atk_value
            * (self.anemo_mv / 100.0)
            * self.anemo_crit_multiplier
            * self.general_defense_multiplier_90
        )
    def calculate_anemo_damage_lv95(self) -> float:
        return (
            self.vesna_total_atk_value
            * (self.anemo_mv / 100.0)
            * self.anemo_crit_multiplier
            * self.general_defense_multiplier_95
        )
    @property
    def vesna_anemo_res_reduction(self) -> float:
        reduction = 0.0

        if self.is_faruzan_active:
            reduction += self.faruzan_anemo_res_reduction

        if self.is_vodyanitsa_active:
            reduction += self.vodyanitsa_anemo_res_reduction

        if (
            self.is_odette_active
            and self.current_configuration["constellations"].get("odette", 0) >= 2
        ):
            reduction += self.odette_C2_anemo_res_reduction

        return reduction
    @property
    def vesna_cryo_res_reduction(self) -> float:
        reduction = 0.0

        if self.is_vodyanitsa_active:
            reduction += self.vodyanitsa_cryo_res_reduction

        if (
            self.is_odette_active
            and self.current_configuration["constellations"].get("odette", 0) >= 2
        ):
            reduction += self.odette_C2_cryo_res_reduction

        if self.is_faruzan_active:
            reduction += self.faruzan_VV_set_cryo_res_reduction

        return reduction
    @property
    def vesna_total_stellar_damage(self) -> float:
        total_atk = self.vesna_total_atk_value

        if self.vesna_constellation >= 2.0:
            total_atk += (
                self.vesna_base_atk_value
                * (1.0 + self.vesna_atk_percent_value / 100.0)
                * self.vesna_C2_atk_value
                / 100.0
            )

        e_damage_mv = self.e_stellar_mv

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

        if self.vesna_constellation >= 1.0:
            total_mv += self.vesna_C1_additional_stellar_mv

        return (
            (
                (
                    total_atk
                    * (total_mv / 100.0)
                    * self.stellar_damage_multiplier
                    * (
                        1.0
                        + (
                            self.vesna_talent_stellar_damage_bonus
                            + self.active_odette_talent_stellar_damage_bonus
                        ) / 100.0
                    )
                    + self.active_vodyanitsa_stellar_quills_flat_damage
                )
                * self.stellar_crit_multiplier
            )
            * self.calculate_res_multiplier(
                10.0,
                self.vesna_anemo_res_reduction,
            )
        )
    def calculate_vortex_proc_damage(self, level: int) -> float:
        if level == 90:
            level_modifier = self.lv90_modifier
        elif level == 95:
            level_modifier = self.lv95_modifier
        else:
            raise ValueError(f"Unsupported enemy level: {level}")

        return (
            (
                level_modifier * 0.75 * 0.6
                * self.stellar_damage_multiplier
                * (
                    1.0
                    + (
                        self.vesna_talent_stellar_damage_bonus
                        + self.active_odette_talent_stellar_damage_bonus
                    ) / 100.0
                )
                + self.active_vodyanitsa_stellar_quills_flat_damage
            )
            * self.calculate_res_multiplier(
                10.0,
                self.vesna_cryo_res_reduction,
            )
        )
    def calculate_vortex_explosion_damage(self, level: int) -> float:
        if level == 90:
            level_modifier = self.lv90_modifier
        elif level == 95:
            level_modifier = self.lv95_modifier
        else:
            raise ValueError(f"Unsupported character level: {level}")

        return (
            (
                level_modifier * 3.0 * 0.6
                * self.stellar_damage_multiplier
                * (
                    1.0
                    + (
                        self.vesna_talent_stellar_damage_bonus
                        + self.active_odette_talent_stellar_damage_bonus
                    ) / 100.0
                )
                + self.active_vodyanitsa_stellar_quills_flat_damage
            )
            * self.calculate_res_multiplier(
                10.0,
                self.vesna_cryo_res_reduction,
            )
        )
    def calculate_vesna_total_vortex_damage(self, level: int) -> float:
        return (
            self.calculate_vortex_proc_damage(level) * self.vortex_procs
            + self.calculate_vortex_explosion_damage(level)
            * self.vortex_explosions
        )    
    def calculate_total_vesna_damage(self, verbose: bool = False) -> float:
        anemo_damage = self.calculate_anemo_damage_lv95()
        stellar_damage = self.vesna_total_stellar_damage
        vortex_damage = self.calculate_vesna_total_vortex_damage(95)

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
    

    # 11. ODETTE – DAMAGE CALCULATIONS
    def calculate_odette_stellar_damage(
        self,mv: float,atk: float,em_multiplier: float,crit_multiplier: float = 0.0,) -> float:
        cryo_resistance_multiplier = self.calculate_cryo_res_multiplier()

        damage = (atk * (mv / 100.0) * em_multiplier + self.active_vodyanitsa_stellar_quills_flat_damage)

        return damage * crit_multiplier * cryo_resistance_multiplier

    # 11.1 ON-FIELD – Coda Finisher Hit
    @property
    def odette_on_field_Coda_stellar_swirl_damage(self) -> float:
        quills = (self.active_vodyanitsa_stellar_quills_flat_damage * 2 if self.is_vodyanitsa_active else 0.0)
        return self.calculate_odette_stellar_damage(
            mv=self.odette_Coda_stellar_swirl_mv,
            atk=self.odette_on_field_atk,
            em_multiplier=self.odette_em_multiplier,
            crit_multiplier=self.odette_stellar_swirl_crit_multiplier,
            flat_damage=quills,
        )

    # 11.2 ON-FIELD – Stellar Plume Hits
    @property
    def odette_on_field_plume_stellar_swirl_damage(self) -> float:
        quills = (
            self.active_vodyanitsa_stellar_quills_flat_damage * 2
            if self.is_vodyanitsa_active
            else 0.0
        )

        return self.calculate_odette_stellar_damage(
            mv=self.odette_plume_stellar_swirl_mv,
            atk=self.odette_on_field_atk,
            em_multiplier=self.odette_em_multiplier,
            crit_multiplier=self.odette_stellar_swirl_crit_multiplier,
            flat_damage=quills,
        )

    # 11.3 ON-FIELD – Stellar Wing Hits
    @property
    def odette_on_field_wing_stellar_swirl_damage(self) -> float:
        quills = (
            self.active_vodyanitsa_stellar_quills_flat_damage * 2
            if self.is_vodyanitsa_active
            else 0.0
        )

        return self.calculate_odette_stellar_damage(
            mv=self.odette_wing_stellar_swirl_mv,
            atk=self.odette_on_field_atk,
            em_multiplier=self.odette_em_multiplier,
            crit_multiplier=self.odette_stellar_swirl_crit_multiplier,
            flat_damage=quills,
        )




    # 11.4 OFF-FIELD – Stellar Hits
    @property
    def odette_off_field_Coda_stellar_swirl_damage(self) -> float:
        quills = (
            self.active_vodyanitsa_stellar_quills_flat_damage * 2
            if self.is_vodyanitsa_active
            else 0.0
        )

        return self.calculate_odette_stellar_damage(
            mv=self.odette_Coda_stellar_swirl_mv,
            atk=self.odette_off_field_atk,
            em_multiplier=self.odette_off_field_em_multiplier,
            crit_multiplier=self.odette_off_field_stellar_swirl_crit_multiplier,
            flat_damage=quills,
        )


    @property
    def odette_off_field_plume_stellar_swirl_damage(self) -> float:
        quills = (
            self.active_vodyanitsa_stellar_quills_flat_damage * 2
            if self.is_vodyanitsa_active
            else 0.0
        )

        return self.calculate_odette_stellar_damage(
            mv=self.odette_plume_stellar_swirl_mv,
            atk=self.odette_off_field_atk,
            em_multiplier=self.odette_off_field_em_multiplier,
            crit_multiplier=self.odette_off_field_stellar_swirl_crit_multiplier,
            flat_damage=quills,
        )


    @property
    def odette_off_field_wing_stellar_swirl_damage(self) -> float:
        quills = (
            self.active_vodyanitsa_stellar_quills_flat_damage * 2
            if self.is_vodyanitsa_active
            else 0.0
        )

        return self.calculate_odette_stellar_damage(
            mv=self.odette_wing_stellar_swirl_mv,
            atk=self.odette_off_field_atk,
            em_multiplier=self.odette_off_field_em_multiplier,
            crit_multiplier=self.odette_off_field_stellar_swirl_crit_multiplier,
            flat_damage=quills,
        )

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

    @property
    def all_team_configurations(self) -> list[dict]:
        configurations = []

        constellation_options = {
            "vesna": self.VESNA_CONSTELLATIONS,
            "odette": self.ODETTE_CONSTELLATIONS,
            "vodyanitsa": self.VODYANITSA_CONSTELLATIONS,
        }

        for team in self.TEAMS:
            members = team["members"]

            variable_members = [
                member
                for member in ("vesna", "odette", "vodyanitsa")
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

    @property
    def vesna_constellation(self) -> int:
        return int(
            self.current_configuration.get("constellations", {}).get(
                "vesna", 0
            )
        )

    @property
    def odette_constellation(self) -> int:
        return int(
            self.current_configuration.get("constellations", {}).get(
                "odette", 0
            )
        )

    @property
    def vodyanitsa_constellation(self) -> int:
        return int(
            self.current_configuration.get("constellations", {}).get(
                "vodyanitsa", 0
            )
        )

    
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
    




    @property
    def team_atk_percent_buff(self) -> float:
        """ATK% buffs for active team members."""
        buff = 0.0

        if self.is_diona_active:
            buff += self.diona_tom_set_atk_buff

        if self.is_vodyanitsa_active:
            buff += self.vodyanitsa_signature_atk_bonus

        if (
            self.is_odette_active
            and self.current_configuration["constellations"].get("odette", 0) >= 2
        ):
            buff += self.odette_C2_marvelous_splender_stacks_atk_percent * 6

        return buff

    @property
    def team_em_buff_vesna(self) -> float:
        buff = 0.0

        if self.is_diona_active:
            buff += self.diona_C6_EM_value

        if self.is_sucrose_active:
            buff += (
                self.sucrose_talent_catalyst_conversion_em_value
                + self.sucrose_talent_mollis_favonius_em_value
            ) * 0.50

            buff += self.sucrose_instrcutor_em_value * 0.80

        return buff

    @property
    def team_em_buff_odette(self) -> float:
        buff = 0.0

        if (
            self.is_diona_active
        ):
            buff += self.diona_C6_EM_value

        if self.is_sucrose_active:
            buff += (
                self.sucrose_talent_catalyst_conversion_em_value
                + self.sucrose_talent_mollis_favonius_em_value
                + self.sucrose_instrcutor_em_value
            )

        return buff

    @property
    def team_stellar_damage_bonus_vesna(self) -> float:
        """Team-wide Stellar damage bonuses for Vesna."""
        buff = 0.0

        if self.is_odette_active:
            stacks = (
                self.odette_C1_marvelous_splender_stacks
                if self.odette_constellation >= 1
                else self.odette_marvelous_splender_stacks
            )

            buff += self.odette_C0_stellar_damage * stacks
            buff += self.odette_furnace_set_stellar_damage_bonus

        if self.is_diona_active:
            buff += self.diona_C6_stellar_damage_bonus

        if self.is_faruzan_active:
            buff += self.faruzan_breezeborne_r5_stellar_damage_bonus

        if (
            self.is_lumine_active
            and self.current_configuration["constellations"].get("lumine", 0) >= 6
        ):
            buff += 40.0

        return buff    



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

    # CR% and ER% are fixed and are no longer treated
    # as variable distribution dimensions.
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
            # The remaining rolls must fit within the capacity
            # of the irrelevant stats.
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

            # Drei-Linien-Artefakt:
            # 1 Verbesserung auf +4, danach 4 weitere.
            # Vier-Linien-Artefakt: 5 Verbesserungen.
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


def find_best_dps_profile(profiles, line_type, team_config):
    """
    Finds the best artifact profile for a given team configuration.

    Profile order:
    ATK, ATK%, CD%, EM, CR%, ER%
    """
    best_profile = None
    best_dps = float("-inf")
    rotation_time = 19.5

    roll_averages = {
        stat: ARTIFACT_SUBSTATS[stat]["average"]
        for stat in ("ATK", "ATK%", "CD%", "EM", "CR%", "ER%")
    }

    total_profiles = len(profiles)
    print(f"Profiles to evaluate: {total_profiles:,}")

    for index, profile in enumerate(profiles, start=1):
        (
            atk_rolls,
            atk_percent_rolls,
            cd_rolls,
            em_rolls,
            cr_rolls,
            er_rolls,
        ) = profile

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

        vesna = VesnaTeamDPSTheorie(
            flat_attack_value=atk_rolls * roll_averages["ATK"],
            atk_percent=(
                atk_percent_rolls
                * ARTIFACT_SUBSTATS["ATK%"]["average"]
            ),
            crit_damage=(
                cd_rolls
                * ARTIFACT_SUBSTATS["CD%"]["average"]
            ),
            elemental_mastery=em_rolls * roll_averages["EM"],
            crit_rate=crit_rate / 100.0,
            energy_recharge=(
                er_rolls * ARTIFACT_SUBSTATS["ER%"]["average"]
            ),
            team_name=team_config["team_name"],
            current_configuration=team_config.copy(),
        )

        total_damage = vesna.calculate_total_vesna_damage()
        dps = total_damage / rotation_time

        if dps > best_dps:
            best_dps = dps
            best_profile = profile

        if index % 1000 == 0 or index == total_profiles:
            print(
                f"\rEvaluated: {index:,}/{total_profiles:,} profiles",
                end="",
                flush=True,
            )

    print()

    constellations = team_config["constellations"]
    print("DEBUG team_config:", team_config)
    print("DEBUG team_name:", team_config.get("team_name"))
    print("DEBUG config_name:", team_config.get("name"))
    print("DEBUG members:", team_config.get("members"))

    print("\n" + "=" * 60)
    print("BEST ARTIFACT PROFILE")
    print("=" * 60)
    print(f"Team: {team_config['team_name']}")
    print(
        f"Configuration: {team_config['name']} | "
        f"Vesna C{int(constellations.get('vesna', 0))} | "
        f"Odette C{int(constellations.get('odette', 0))} | "
        f"Vodyanitsa C{int(constellations.get('vodyanitsa', 0))}"
    )
    print(f"Line Type: {line_type}")
    print(f"Best Profile (ATK, ATK%, CD%, EM, CR%, ER%): {best_profile}")
    print(f"Maximum Rotation Damage: {best_dps * rotation_time:,.2f}")
    print(f"Maximum Vesna DPS: {best_dps:,.2f}")

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

        best_vesna = VesnaTeamDPSTheorie(
            flat_attack_value=atk_rolls * roll_averages["ATK"],
            atk_percent=(
                atk_percent_rolls
                * ARTIFACT_SUBSTATS["ATK%"]["average"]
            ),
            crit_damage=(
                cd_rolls
                * ARTIFACT_SUBSTATS["CD%"]["average"]
            ),
            elemental_mastery=em_rolls * roll_averages["EM"],
            crit_rate=crit_rate / 100.0,
            energy_recharge=(
                er_rolls * ARTIFACT_SUBSTATS["ER%"]["average"]
            ),
            team_name=team_config["team_name"],
            current_configuration=team_config.copy(),
        )

        print("DEBUG: Team damage calculation erreicht")
        # Team damage calculation
        members = set(team_config["members"])
        print("DEBUG members:", members)
        vesna_rotation_damage = (
            best_vesna.calculate_total_vesna_damage()
        )
        vesna_dps = vesna_rotation_damage / rotation_time

        # Odette - Stellar damage
        odette_on_field_stellar = (
            best_vesna.odette_on_field_Coda_stellar_swirl_damage
            + best_vesna.odette_plume_hits
            * best_vesna.odette_on_field_plume_stellar_swirl_damage
            + best_vesna.odette_wing_hits
            * best_vesna.odette_on_field_wing_stellar_swirl_damage
        )

        odette_off_field_stellar = (
            best_vesna.odette_off_field_Coda_stellar_swirl_damage
            + best_vesna.odette_plume_stellar_hits
            * best_vesna.odette_off_field_plume_stellar_swirl_damage
            + best_vesna.odette_wing_stellar_hits
            * best_vesna.odette_off_field_wing_stellar_swirl_damage
        )

        # Lumine - Cryo and Stellar damage
        lumine_rotation_damage = (
            best_vesna.lumine_stellar_charge_attack_damage
            + best_vesna.lumine_e_skill_cryo_damage_on_field
            + best_vesna.lumine_e_skill_cryo_damage_off_field
            + best_vesna.lumine_ultimate_q_stellar_damage
        )

        print("\n" + "-" * 60)
        print("ODETTE DAMAGE BREAKDOWN")
        print("-" * 60)

        if "odette" in members:
            print(f"On-Field Stellar Damage:  {odette_on_field_stellar:,.2f}")
            print(f"Off-Field Stellar Damage: {odette_off_field_stellar:,.2f}")
        else:
            print(f"On-Field Stellar Damage:  {0.0:,.2f}")
            print(f"Off-Field Stellar Damage: {0.0:,.2f}")

        print("-" * 60)

        odette_rotation_damage = (
            odette_on_field_stellar
            + odette_off_field_stellar
        )
        odette_dps = odette_rotation_damage / rotation_time
        lumine_dps = lumine_rotation_damage / rotation_time

        # DPS contributions from other team members
        diona_dps_value = 5000.0 if "diona" in members else 0.0
        faruzan_dps_value = 15000.0 if "faruzan" in members else 0.0
        sucrose_dps_value = 2500.0 if "sucrose" in members else 0.0
        vodyanitsa_flat_dps = 750.0 if "vodyanitsa" in members else 0.0


        # Total team damage
        vesna_dps = vesna_dps if "vesna" in members else 0.0
        odette_dps = odette_dps if "odette" in members else 0.0
        lumine_dps = lumine_dps if "lumine" in members else 0.0

        team_dps = (
            vesna_dps
            + odette_dps
            + diona_dps_value
            + faruzan_dps_value
            + sucrose_dps_value
            + vodyanitsa_flat_dps
            + lumine_dps
        )
        team_rotation_damage = team_dps * rotation_time
    
        # Final report
        print("TEAM DAMAGE BREAKDOWN")
        print("-" * 60)
        print(f"Rotation Duration:          {rotation_time:.2f} s")
        print(f"Vesna Rotation Damage:      {vesna_rotation_damage:,.2f}")
        print(f"Vesna DPS:                  {vesna_dps:,.2f}")
        print(f"Odette Stellar Damage:      {odette_rotation_damage:,.2f}")
        print(f"Odette DPS:                 {odette_dps:,.2f}")
        print(f"Lumine Rotation Damage:     {lumine_rotation_damage:,.2f}")
        print(f"Lumine DPS:                 {lumine_dps:,.2f}")
        print(f"Diona DPS:                  {diona_dps_value:,.2f}")
        print(f"Faruzan DPS:                {faruzan_dps_value:,.2f}")
        print(f"Sucrose DPS:                {sucrose_dps_value:,.2f}")
        print(f"Vodyanitsa DPS:             {vodyanitsa_flat_dps:,.2f}")
        print("-" * 60)
        print(f"Total Team Rotation Damage: {team_rotation_damage:,.2f}")
        print(f"TOTAL TEAM DPS:             {team_dps:,.2f}")
        print("=" * 60)

    return best_profile, best_dps



# 13. PROGRAM ENTRY POINT – OUTSIDE THE CLASS
if __name__ == "__main__":
    log_path = Path(__file__).with_name("vesna_calc.log")
    log_file = log_path.open("w", encoding="utf-8")

    sys.stdout = Tee(sys.stdout, log_file)
    atexit.register(log_file.close)
    calculator = VesnaTeamDPSTheorie()
    line_type = "3_line"

    print("\n=== Loading Combined Artifact Profiles ===")
    combined_profiles = load_or_calculate_profiles(line_type)

    print(f"\nTotal Artifact Profiles: {len(combined_profiles):,}")
    print("\n=== Starting Team Optimization ===")

    total_configurations = len(calculator.all_team_configurations)

    for index, config in enumerate(
        calculator.all_team_configurations,
        start=1,
    ):
        print(
            f"\n{'=' * 60}\n"
            f"Configuration {index}/{total_configurations}"
        )

        best_profile, best_dps = find_best_dps_profile(
            combined_profiles,
            line_type,
            config,
        )
