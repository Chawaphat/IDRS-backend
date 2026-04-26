from enum import Enum


class UserRole(str, Enum):
    dentist = "dentist"
    assistant = "assistant"


class AllergyStatusType(str, Enum):
    no = "no"
    yes = "yes"
    dont_know = "dont_know"


class PatientExpectationsType(str, Enum):
    chewing = "chewing"
    esthetic = "esthetic"
    health = "health"
    phonetics = "phonetics"


class FacialSymmetryType(str, Enum):
    symmetry = "symmetry"
    asymmetry = "asymmetry"


class FacialProfileType(str, Enum):
    convex = "convex"
    straight = "straight"
    concave = "concave"


class JointPainType(str, Enum):
    function = "function"
    palpation = "palpation"


class JointSoundType(str, Enum):
    no = "no"
    clicking = "clicking"
    crepitus = "crepitus"
    popping = "popping"


class JawDeviationType(str, Enum):
    none = "none"
    to_left = "to_left"
    to_right = "to_right"


class HabitType(str, Enum):
    nail_biting = "nail_biting"
    bruxism = "bruxism"
    clenching = "clenching"
    tongue_thrust = "tongue_thrust"


class OcclusalPlaneType(str, Enum):
    parallel = "parallel"
    canted_right = "canted_right"
    canted_left = "canted_left"


class MidlineDiscrepancyType(str, Enum):
    symmetric = "symmetric"
    right_shift = "right_shift"
    left_shift = "left_shift"


class LipThicknessType(str, Enum):
    full = "full"
    average = "average"
    thin = "thin"


class LipLengthType(str, Enum):
    long = "long"
    average = "average"
    short = "short"


class NasolabialAngleType(str, Enum):
    normal = "normal"
    prominent_maxilla = "prominent_maxilla"
    retruded_maxilla = "retruded_maxilla"


class FacialConditionType(str, Enum):
    nasolabial_fold = "nasolabial_fold"
    prominent_chin = "prominent_chin"
    drooping_commissure = "drooping_commissure"
    thin_lips = "thin_lips"


class BiteType(str, Enum):
    normal_bite = "normal_bite"
    deep_bite = "deep_bite"
    edge_to_edge = "edge_to_edge"
    crossbite = "crossbite"


class SurfaceEnum(str, Enum):
    B = "B"
    O = "O"
    M = "M"
    L = "L"
    D = "D"


class CariesType(str, Enum):
    none = "none"
    caries = "caries"
    filling = "filling"
    secondary_caries = "secondary_caries"


class ContactType(str, Enum):
    mip = "mip"
    premature = "premature"
    protrusive = "protrusive"
    working = "working"
    non_working = "non_working"


class MolarType(str, Enum):
    class_i = "class_i"
    class_ii = "class_ii"
    class_iii = "class_iii"


class ImageCategory(str, Enum):
    intraoral = "intraoral"
    panoramic_xray = "panoramic_xray"
    other = "other"
