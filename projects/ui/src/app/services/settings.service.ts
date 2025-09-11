import { Injectable, signal } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class SettingsService {
  private readonly API_KEY_TONGYI_STORAGE_KEY = 'pixelda_tongyi_api_key';
  private readonly API_KEY_DOUBAO_STORAGE_KEY = 'pixelda_doubao_api_key';
  private readonly ACTIVE_API_KEY_STORAGE_KEY = 'pixelda_active_api_key';
  private readonly LANGUAGE_STORAGE_KEY = 'pixelda_language';
  private tongyiApiKeySignal = signal<string>('');
  private doubaoApiKeySignal = signal<string>('');
  private activeModel = signal<string>('tongyi');
  private languageSignal = signal<string>('en');

  constructor() {
    const storedKey = localStorage.getItem(this.API_KEY_TONGYI_STORAGE_KEY);
    if (storedKey) {
      this.tongyiApiKeySignal.set(storedKey);
    }
    const storedDoubaoKey = localStorage.getItem(this.API_KEY_DOUBAO_STORAGE_KEY);
    if (storedDoubaoKey) {
      this.doubaoApiKeySignal.set(storedDoubaoKey);
    }
    const storedActive = localStorage.getItem(this.ACTIVE_API_KEY_STORAGE_KEY);
    if (storedActive) {
      this.activeModel.set(storedActive);
    }
    const storedLanguage = localStorage.getItem(this.LANGUAGE_STORAGE_KEY);
    if (storedLanguage) {
      this.languageSignal.set(storedLanguage);
    }
  }

  readonly tongyiApiKey = this.tongyiApiKeySignal.asReadonly();
  readonly doubaoApiKey = this.doubaoApiKeySignal.asReadonly();
  readonly activeApiKey = this.activeModel.asReadonly();
  readonly language = this.languageSignal.asReadonly();

  setTongyiApiKey(apiKey: string): void {
    this.tongyiApiKeySignal.set(apiKey);
    localStorage.setItem(this.API_KEY_TONGYI_STORAGE_KEY, apiKey);
  }

  setDoubaoApiKey(apiKey: string): void {
    this.doubaoApiKeySignal.set(apiKey);
    localStorage.setItem(this.API_KEY_DOUBAO_STORAGE_KEY, apiKey);
  }

  getTongyiApiKey(): string {
    return this.tongyiApiKeySignal();
  }

  getDoubaoApiKey(): string {
    return this.doubaoApiKeySignal();
  }

  setActiveApiKey(type: string): void {
    this.activeModel.set(type);
    localStorage.setItem(this.ACTIVE_API_KEY_STORAGE_KEY, type);
  }

  getActiveModel(): string {
    return this.activeModel();
  }

  getCurrentActiveApiKey(): string {
    const active = this.activeModel();
    if (active === 'doubao') {
      return this.doubaoApiKeySignal();
    }
    return this.tongyiApiKeySignal();
  }

  clearTongyiApiKey(): void {
    this.tongyiApiKeySignal.set('');
    localStorage.removeItem(this.API_KEY_TONGYI_STORAGE_KEY);
  }

  clearDoubaoApiKey(): void {
    this.doubaoApiKeySignal.set('');
    localStorage.removeItem(this.API_KEY_DOUBAO_STORAGE_KEY);
  }

  hasTongyiApiKey(): boolean {
    return this.tongyiApiKeySignal().length > 0;
  }

  hasDoubaoApiKey(): boolean {
    return this.doubaoApiKeySignal().length > 0;
  }

  hasAnyApiKey(): boolean {
    return this.hasTongyiApiKey() || this.hasDoubaoApiKey();
  }

  getMaskedTongyiApiKey(): string {
    const key = this.tongyiApiKeySignal();
    if (!key) return '';
    return '*'.repeat(12);
  }

  getMaskedDoubaoApiKey(): string {
    const key = this.doubaoApiKeySignal();
    if (!key) return '';
    return '*'.repeat(12);
  }

  setLanguage(language: string): void {
    this.languageSignal.set(language);
    localStorage.setItem(this.LANGUAGE_STORAGE_KEY, language);
  }

  getLanguage(): string {
    return this.languageSignal();
  }
}
