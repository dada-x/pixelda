import { Component } from '@angular/core';

@Component({
  selector: 'app-icon-clock',
  standalone: true,
  template: `
    <svg width="16" height="16" viewBox="0 0 24 24" class="icon">
      <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="2" />
      <path
        d="M12 6v6l4 2"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
    </svg>
  `,
  styles: [
    `
      .icon {
        display: inline-block;
        vertical-align: middle;
      }
    `,
  ],
})
export class IconClockComponent {}
