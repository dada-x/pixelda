import { Injectable } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class TranslationService {
  private currentLanguageSubject = new BehaviorSubject<string>('en');
  public currentLanguage$ = this.currentLanguageSubject.asObservable();

  constructor(private translate: TranslateService) {
    this.initializeLanguage();
  }

  private initializeLanguage(): void {
    this.translate.setDefaultLang('en');

    const savedLanguage = localStorage.getItem('pixelda_language');
    const browserLang = this.translate.getBrowserLang();
    const defaultLang = savedLanguage || (browserLang?.match(/en|zh/) ? browserLang : 'en');

    this.setLanguage(defaultLang);
  }

  setLanguage(lang: string): void {
    this.translate.use(lang);
    this.currentLanguageSubject.next(lang);
    localStorage.setItem('pixelda_language', lang);
  }

  getCurrentLanguage(): string {
    return this.currentLanguageSubject.value;
  }

  getAvailableLanguages(): { code: string; name: string }[] {
    return [
      { code: 'en', name: 'English' },
      { code: 'zh', name: '中文' },
    ];
  }
}
