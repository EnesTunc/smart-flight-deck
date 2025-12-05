/// Checklist Role - Pilot Flying vs First Officer
enum ChecklistRole {
  pilotFlying,
  firstOfficer,
}

extension ChecklistRoleExtension on ChecklistRole {
  String get displayName {
    switch (this) {
      case ChecklistRole.pilotFlying:
        return 'PILOT FLYING';
      case ChecklistRole.firstOfficer:
        return 'FIRST OFFICER';
    }
  }

  String get shortName {
    switch (this) {
      case ChecklistRole.pilotFlying:
        return 'PF';
      case ChecklistRole.firstOfficer:
        return 'FO';
    }
  }

  String get description {
    switch (this) {
      case ChecklistRole.pilotFlying:
        return 'You read challenges,\nTTS responds';
      case ChecklistRole.firstOfficer:
        return 'TTS reads challenges,\nYou respond';
    }
  }

  // Convert to string for storage
  String toStorageString() {
    switch (this) {
      case ChecklistRole.pilotFlying:
        return 'pilot_flying';
      case ChecklistRole.firstOfficer:
        return 'first_officer';
    }
  }

  // Convert from string
  static ChecklistRole fromStorageString(String value) {
    switch (value) {
      case 'pilot_flying':
        return ChecklistRole.pilotFlying;
      case 'first_officer':
        return ChecklistRole.firstOfficer;
      default:
        return ChecklistRole.firstOfficer; // Default
    }
  }
}
