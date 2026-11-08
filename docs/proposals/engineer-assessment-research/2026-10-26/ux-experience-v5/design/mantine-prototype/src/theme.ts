import { createTheme } from '@mantine/core';
import tokens from '../../tokens.json';

// Candidate palette mapped from ../tokens.json. The library theme is the UI skin;
// product claims, timing, media, purpose and data rules stay in project contracts.
export const theme = createTheme({
  primaryColor: 'assessment',
  primaryShade: 7,
  colors: {
    assessment: ['#eef4fb','#dce9f7','#bed3ee','#97b9e1','#709ed1','#4d83bd','#3068a2',tokens.color.action.$value,'#103b70','#0b2d57'],
  },
  fontFamily: tokens.type.body.$value.join(', '),
  headings: { fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif', fontWeight: '700' },
  defaultRadius: 'sm',
  radius: { xs: '3px', sm: '6px', md: '10px', lg: '16px', xl: '24px' },
  spacing: { xs: '4px', sm: '8px', md: '16px', lg: '24px', xl: '32px' },
  focusRing: 'auto',
});
