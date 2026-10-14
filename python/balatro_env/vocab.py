"""Stable id vocabularies for observation tokenization.

Keys are vanilla Balatro center keys in the game's own `order` (game.lua P_CENTERS). Ids are positions in
these tuples + 1 (0 = empty/padding, len + 1 = unknown key), so they are identical across processes and
machines. Append new keys at the end only; never reorder, or previously trained models break.
"""

JOKER_KEYS = (
    "j_joker", "j_greedy_joker", "j_lusty_joker", "j_wrathful_joker", "j_gluttenous_joker",
    "j_jolly", "j_zany", "j_mad", "j_crazy", "j_droll", "j_sly", "j_wily", "j_clever", "j_devious",
    "j_crafty", "j_half", "j_stencil", "j_four_fingers", "j_mime", "j_credit_card", "j_ceremonial",
    "j_banner", "j_mystic_summit", "j_marble", "j_loyalty_card", "j_8_ball", "j_misprint", "j_dusk",
    "j_raised_fist", "j_chaos", "j_fibonacci", "j_steel_joker", "j_scary_face", "j_abstract",
    "j_delayed_grat", "j_hack", "j_pareidolia", "j_gros_michel", "j_even_steven", "j_odd_todd",
    "j_scholar", "j_business", "j_supernova", "j_ride_the_bus", "j_space", "j_egg", "j_burglar",
    "j_blackboard", "j_runner", "j_ice_cream", "j_dna", "j_splash", "j_blue_joker", "j_sixth_sense",
    "j_constellation", "j_hiker", "j_faceless", "j_green_joker", "j_superposition", "j_todo_list",
    "j_cavendish", "j_card_sharp", "j_red_card", "j_madness", "j_square", "j_seance", "j_riff_raff",
    "j_vampire", "j_shortcut", "j_hologram", "j_vagabond", "j_baron", "j_cloud_9", "j_rocket",
    "j_obelisk", "j_midas_mask", "j_luchador", "j_photograph", "j_gift", "j_turtle_bean",
    "j_erosion", "j_reserved_parking", "j_mail", "j_to_the_moon", "j_hallucination",
    "j_fortune_teller", "j_juggler", "j_drunkard", "j_stone", "j_golden", "j_lucky_cat",
    "j_baseball", "j_bull", "j_diet_cola", "j_trading", "j_flash", "j_popcorn", "j_trousers",
    "j_ancient", "j_ramen", "j_walkie_talkie", "j_selzer", "j_castle", "j_smiley", "j_campfire",
    "j_ticket", "j_mr_bones", "j_acrobat", "j_sock_and_buskin", "j_swashbuckler", "j_troubadour",
    "j_certificate", "j_smeared", "j_throwback", "j_hanging_chad", "j_rough_gem", "j_bloodstone",
    "j_arrowhead", "j_onyx_agate", "j_glass", "j_ring_master", "j_flower_pot", "j_blueprint",
    "j_wee", "j_merry_andy", "j_oops", "j_idol", "j_seeing_double", "j_matador", "j_hit_the_road",
    "j_duo", "j_trio", "j_family", "j_order", "j_tribe", "j_stuntman", "j_invisible",
    "j_brainstorm", "j_satellite", "j_shoot_the_moon", "j_drivers_license", "j_cartomancer",
    "j_astronomer", "j_burnt", "j_bootstraps", "j_caino", "j_triboulet", "j_yorick", "j_chicot",
    "j_perkeo",
)

CONSUMABLE_KEYS = (
    "c_fool", "c_magician", "c_high_priestess", "c_empress", "c_emperor", "c_heirophant",
    "c_lovers", "c_chariot", "c_justice", "c_hermit", "c_wheel_of_fortune", "c_strength",
    "c_hanged_man", "c_death", "c_temperance", "c_devil", "c_tower", "c_star", "c_moon", "c_sun",
    "c_judgement", "c_world", "c_mercury", "c_venus", "c_earth", "c_mars", "c_jupiter", "c_saturn",
    "c_uranus", "c_neptune", "c_pluto", "c_planet_x", "c_ceres", "c_eris", "c_familiar", "c_grim",
    "c_incantation", "c_talisman", "c_aura", "c_wraith", "c_sigil", "c_ouija", "c_ectoplasm",
    "c_immolate", "c_ankh", "c_deja_vu", "c_hex", "c_trance", "c_medium", "c_cryptid", "c_soul",
    "c_black_hole",
)

VOUCHER_KEYS = (
    "v_overstock_norm", "v_overstock_plus", "v_clearance_sale", "v_liquidation", "v_hone",
    "v_glow_up", "v_reroll_surplus", "v_reroll_glut", "v_crystal_ball", "v_omen_globe",
    "v_telescope", "v_observatory", "v_grabber", "v_nacho_tong", "v_wasteful", "v_recyclomancy",
    "v_tarot_merchant", "v_tarot_tycoon", "v_planet_merchant", "v_planet_tycoon", "v_seed_money",
    "v_money_tree", "v_blank", "v_antimatter", "v_magic_trick", "v_illusion", "v_hieroglyph",
    "v_petroglyph", "v_directors_cut", "v_retcon", "v_paint_brush", "v_palette",
)

BOOSTER_KEYS = (
    "p_arcana_normal_1", "p_arcana_normal_2", "p_arcana_normal_3", "p_arcana_normal_4",
    "p_arcana_jumbo_1", "p_arcana_jumbo_2", "p_arcana_mega_1", "p_arcana_mega_2",
    "p_celestial_normal_1", "p_celestial_normal_2", "p_celestial_normal_3", "p_celestial_normal_4",
    "p_celestial_jumbo_1", "p_celestial_jumbo_2", "p_celestial_mega_1", "p_celestial_mega_2",
    "p_standard_normal_1", "p_standard_normal_2", "p_standard_normal_3", "p_standard_normal_4",
    "p_standard_jumbo_1", "p_standard_jumbo_2", "p_standard_mega_1", "p_standard_mega_2",
    "p_buffoon_normal_1", "p_buffoon_normal_2", "p_buffoon_jumbo_1", "p_buffoon_mega_1",
    "p_spectral_normal_1", "p_spectral_normal_2", "p_spectral_jumbo_1", "p_spectral_mega_1",
)

# Playing-card enhancements as reported by the bridge (`card.ability.name`) and by center key.
ENHANCEMENTS = (
    ("m_bonus", "Bonus"), ("m_mult", "Mult"), ("m_wild", "Wild Card"), ("m_glass", "Glass Card"),
    ("m_steel", "Steel Card"), ("m_stone", "Stone Card"), ("m_gold", "Gold Card"), ("m_lucky", "Lucky Card"),
)

# Shop/pack item sets (`ability.set` / `center.set`).
ITEM_SETS = ("Joker", "Tarot", "Planet", "Spectral", "Voucher", "Booster", "Default", "Enhanced")


def build_index(keys: tuple[str, ...]) -> dict[str, int]:
    """Map each key to a stable 1-based id."""
    return {k: i + 1 for i, k in enumerate(keys)}


JOKER_IDS = build_index(JOKER_KEYS)
CONSUMABLE_IDS = build_index(CONSUMABLE_KEYS)
ITEM_SET_IDS = build_index(ITEM_SETS)
ENHANCEMENT_IDS = {alias: i + 1 for i, pair in enumerate(ENHANCEMENTS) for alias in pair}


def lookup(table: dict[str, int], key: str | None) -> int:
    """Stable id for `key`: 0 for None/empty, len(table distinct ids) + 1 for unknown keys."""
    if not key:
        return 0
    return table.get(key, max(table.values()) + 1)
