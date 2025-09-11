import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { CommonModule } from '@angular/common';
import { TranslateModule } from '@ngx-translate/core';

@Component({
  selector: 'app-layout',
  standalone: true,
  imports: [RouterOutlet, CommonModule, TranslateModule],
  templateUrl: './layout.component.html',
  styleUrls: ['./layout.component.scss'],
})
export class LayoutComponent {
  sidebarCollapsed = signal(false);

  menuItems = [
    { label: 'NAVIGATION.WHATS_NEW', icon: 'star', link: '/' },
    {
      label: 'NAVIGATION.GENERATE',
      icon: 'pencil',
      link: '/generate',
      subItems: [
        { label: 'NAVIGATION.IMAGE', icon: 'image', link: '/generate/image' },
        { label: 'NAVIGATION.ANIMATION', icon: 'animation', link: '/generate/animation' },
        { label: 'NAVIGATION.SPRITES', icon: 'sprite-sheet', link: '/generate/sprite-sheet' },
        { label: 'NAVIGATION.SOUND', icon: 'sound', link: '/generate/sound' },
      ],
    },
    { label: 'NAVIGATION.HISTORY', icon: 'clock', link: '/history' },
    { label: 'NAVIGATION.SETTINGS', icon: 'gear', link: '/settings' },
  ];

  toggleSidebar() {
    this.sidebarCollapsed.set(!this.sidebarCollapsed());
  }
}
