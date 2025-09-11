import { Component, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { SettingsService } from '../../services/settings.service';
import { TranslationService } from '../../services/translation.service';
import { TranslateModule } from '@ngx-translate/core';

@Component({
  selector: 'app-settings',
  standalone: true,
  imports: [CommonModule, FormsModule, TranslateModule],
  templateUrl: './settings.component.html',
  styleUrls: ['./settings.component.scss'],
})
export class SettingsComponent {
  tongyiApiKeyInput = signal('');
  doubaoApiKeyInput = signal('');
  showTongyiApiKey = signal(false);
  showDoubaoApiKey = signal(false);
  activeApiKey = signal('tongyi');
  selectedLanguage = signal('en');

  constructor(
    public settingsService: SettingsService,
    private translationService: TranslationService
  ) {
    this.tongyiApiKeyInput.set(this.settingsService.getMaskedTongyiApiKey());
    this.doubaoApiKeyInput.set(this.settingsService.getMaskedDoubaoApiKey());
    this.activeApiKey.set(this.settingsService.getActiveModel());
    this.selectedLanguage.set(this.settingsService.getLanguage());
  }

  toggleTongyiApiKeyVisibility(): void {
    this.showTongyiApiKey.update((show) => !show);
    if (this.showTongyiApiKey()) {
      this.tongyiApiKeyInput.set(this.settingsService.getTongyiApiKey());
    } else {
      this.tongyiApiKeyInput.set(this.settingsService.getMaskedTongyiApiKey());
    }
  }

  toggleDoubaoApiKeyVisibility(): void {
    this.showDoubaoApiKey.update((show) => !show);
    if (this.showDoubaoApiKey()) {
      this.doubaoApiKeyInput.set(this.settingsService.getDoubaoApiKey());
    } else {
      this.doubaoApiKeyInput.set(this.settingsService.getMaskedDoubaoApiKey());
    }
  }

  saveApiKey(): void {
    const currentInput = this.tongyiApiKeyInput();

    let apiKeyToSave: string;

    if (this.showTongyiApiKey()) {
      apiKeyToSave = currentInput;
    } else {
      if (currentInput && !currentInput.includes('*')) {
        apiKeyToSave = currentInput;
      } else {
        apiKeyToSave = currentInput || this.settingsService.getTongyiApiKey();
      }
    }

    if (apiKeyToSave && apiKeyToSave.trim()) {
      this.settingsService.setTongyiApiKey(apiKeyToSave.trim());
      this.tongyiApiKeyInput.set(this.settingsService.getMaskedTongyiApiKey());
      this.showTongyiApiKey.set(false);
    }
  }

  saveDoubaoApiKey(): void {
    const currentInput = this.doubaoApiKeyInput();

    let apiKeyToSave: string;

    if (this.showDoubaoApiKey()) {
      apiKeyToSave = currentInput;
    } else {
      if (currentInput && !currentInput.includes('*')) {
        apiKeyToSave = currentInput;
      } else {
        apiKeyToSave = currentInput || this.settingsService.getDoubaoApiKey();
      }
    }

    if (apiKeyToSave && apiKeyToSave.trim()) {
      this.settingsService.setDoubaoApiKey(apiKeyToSave.trim());
      this.doubaoApiKeyInput.set(this.settingsService.getMaskedDoubaoApiKey());
      this.showDoubaoApiKey.set(false);
    }
  }

  clearTongyiApiKey(): void {
    this.settingsService.clearTongyiApiKey();
    this.tongyiApiKeyInput.set('');
    this.showTongyiApiKey.set(false);
  }

  clearDoubaoApiKey(): void {
    this.settingsService.clearDoubaoApiKey();
    this.doubaoApiKeyInput.set('');
    this.showDoubaoApiKey.set(false);
  }

  onApiKeyInputChange(value: string): void {
    this.tongyiApiKeyInput.set(value);
  }

  onDoubaoApiKeyInputChange(value: string): void {
    this.doubaoApiKeyInput.set(value);
  }

  setActiveApiKey(type: string): void {
    this.activeApiKey.set(type);
    this.settingsService.setActiveApiKey(type);
  }

  getAvailableLanguages() {
    return this.translationService.getAvailableLanguages();
  }

  onLanguageChange(language: string): void {
    this.selectedLanguage.set(language);
    this.settingsService.setLanguage(language);
    this.translationService.setLanguage(language);
  }
}
