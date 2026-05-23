from enum import Enum


class UserRole(str, Enum):
    dentist = "dentist"
    assistant = "assistant"
    admin = "admin"


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


class ToothTypeEnum(str, Enum):
    edentulous = "edentulous"
    primary = "primary"
    permanent = "permanent"
    implant = "implant"

class EdentulousTypeEnum(str, Enum):
    missing = "missing"
    extraction = "extraction"
    embedded = "embedded"
    impacted = "impacted"

class CariesDepthEnum(str, Enum):
    enamel = "enamel"
    dentine = "dentine"
    pulp = "pulp"

class ToothSurfaceEnum(str, Enum):
    M = "M"
    D = "D"
    B = "B"
    L = "L"
    P = "P"
    O = "O"

class FillingMaterialEnum(str, Enum):
    composite = "composite"
    amalgam = "amalgam"
    gic = "gic"
    temporary = "temporary"

class MobilityGradeEnum(str, Enum):
    normal = "normal"
    M1 = "M1"
    M2 = "M2"
    M3 = "M3"

class EptResultEnum(str, Enum):
    positive = "positive"
    negative = "negative"

class RootCanalTreatedEnum(str, Enum):
    no = "no"
    medicated = "medicated"
    incomplete = "incomplete"
    completed = "completed"

class RestorationTypeEnum(str, Enum):
    crown = "crown"
    bridge = "bridge"
    veneer = "veneer"
    onlay = "onlay"
    overlay = "overlay"
    post_and_core = "post_and_core"
    vonlay = "vonlay"

class RestorationMaterialEnum(str, Enum):
    zirconia = "zirconia"
    lithium_disilicate = "lithium_disilicate"
    full_metal = "full_metal"
    pfm = "pfm"
    pfz = "pfz"
    emax = "emax"

class PostTypeEnum(str, Enum):
    metal_post = "metal_post"
    fiber_post = "fiber_post"

class ImplantComponentEnum(str, Enum):
    crown = "crown"
    bridge = "bridge"
    healing_abutment = "healing_abutment"
    cover_screw = "cover_screw"

class RetentionTypeEnum(str, Enum):
    cement_retained = "cement_retained"
    screw_retained = "screw_retained"

class RidgeHeightType(str, Enum):
    high = "high"
    low_flat = "low_flat"
    knife_edge = "knife_edge"


class RidgeWidthType(str, Enum):
    round = "round"
    narrow = "narrow"


class JawSizeType(str, Enum):
    small = "small"
    medium = "medium"
    large = "large"


class RidgeShapeType(str, Enum):
    u_shape = "u_shape"
    v_shape = "v_shape"
    undercut = "undercut"
    flat = "flat"


class RidgeRelationType(str, Enum):
    class_i = "class_i"
    class_ii = "class_ii"
    class_iii = "class_iii"
    crossbite = "crossbite"


class RidgeParallelismType(str, Enum):
    parallel = "parallel"
    divergent = "divergent"


class InterridgeSpaceType(str, Enum):
    sufficient = "sufficient"
    insufficient = "insufficient"


class ArchFormType(str, Enum):
    square = "square"
    taper = "taper"
    ovoid = "ovoid"


class PalatalVaultType(str, Enum):
    average = "average"
    steep = "steep"
    v_shape = "v_shape"
    shallow = "shallow"


class PalatalThroatFormType(str, Enum):
    class_i = "class_i"
    class_ii = "class_ii"
    class_iii = "class_iii"


class TongueSizeType(str, Enum):
    small = "small"
    medium = "medium"
    large = "large"


class TonguePositionType(str, Enum):
    normal = "normal"
    retracted = "retracted"


class SalivaAmountType(str, Enum):
    normal = "normal"
    xerostomia = "xerostomia"


class SalivaConsistencyType(str, Enum):
    thick = "thick"
    thin = "thin"


class LipMobilityType(str, Enum):
    normal = "normal"
    highly_active = "highly_active"
    relatively_inactive = "relatively_inactive"


class FacialMuscleToneType(str, Enum):
    tense = "tense"
    average = "average"
    flaccid = "flaccid"


class MentalAttitudeType(str, Enum):
    philosophical = "philosophical"
    exacting = "exacting"
    hysterical = "hysterical"
    indifferent = "indifferent"
