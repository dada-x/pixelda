import { Component, OnInit, OnDestroy } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { TranslationService } from './services/translation.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet],
  template: ` <router-outlet /> `,
  styles: [],
})
export class App implements OnInit, OnDestroy {
  private languageSubscription: Subscription = new Subscription();

  constructor(private translationService: TranslationService) {}

  ngOnInit(): void {
    this.updateLanguageClass(this.translationService.getCurrentLanguage());

    this.languageSubscription = this.translationService.currentLanguage$.subscribe((lang) => {
      this.updateLanguageClass(lang);
    });
  }

  ngOnDestroy(): void {
    this.languageSubscription.unsubscribe();
  }

  private updateLanguageClass(lang: string): void {
    document.documentElement.classList.remove('lang-en', 'lang-zh');
    document.body.classList.remove('lang-en', 'lang-zh');

    document.documentElement.classList.add(`lang-${lang}`);
    document.body.classList.add(`lang-${lang}`);
    document.documentElement.setAttribute('lang', lang);
  }
}
