import { Routes } from '@angular/router';
import { LayoutComponent } from './components/layout.component';
import { HomeComponent } from './components/home.component';
import { ImageComponent } from './components/generation/image.component';
import { AnimationComponent } from './components/generation/animation.component';
import { SpriteSheetComponent } from './components/generation/sprite-sheet.component';
import { MusicComponent } from './components/generation/music.component';
import { HistoryComponent } from './components/common/history.component';
import { SettingsComponent } from './components/common/settings.component';

export const routes: Routes = [
  {
    path: '',
    component: LayoutComponent,
    children: [
      { path: '', component: HomeComponent },
      {
        path: 'generate',
        children: [
          { path: '', component: HomeComponent },
          { path: 'image', component: ImageComponent },
          { path: 'animation', component: AnimationComponent },
          { path: 'sprite-sheet', component: SpriteSheetComponent },
          { path: 'music', component: MusicComponent },
        ],
      },
      { path: 'history', component: HistoryComponent },
      { path: 'settings', component: SettingsComponent },
    ],
  },
];
