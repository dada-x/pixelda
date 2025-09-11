import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { SettingsService } from '../services/settings.service';

export const apiKeyInterceptor: HttpInterceptorFn = (req, next) => {
  const settingsService = inject(SettingsService);

  if (req.url.startsWith('/api') && settingsService.hasAnyApiKey()) {
    const apiKey = settingsService.getCurrentActiveApiKey();
    const clonedRequest = req.clone({
      setHeaders: {
        'X-API-Key': apiKey,
      },
    });
    return next(clonedRequest);
  }

  return next(req);
};
