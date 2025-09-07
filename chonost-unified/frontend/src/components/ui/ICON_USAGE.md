# Icon Component Usage Guide

## Overview

The enhanced Icon component supports both Lucide icons and Simple Icons logos with a unified API.

## Installation

Make sure you have the required dependencies installed:

```bash
npm install lucide-react simple-icons
```

## Usage

### Basic Usage

```tsx
import { Icon } from '@chonost/ui';

// Lucide icon
<Icon name="lucide:edit-3" size={24} color="blue" />

// Logo icon
<Icon name="logo:github" size={24} />
```

### Props

- `name` (string, required): Icon name with prefix
  - `lucide:icon-name` for Lucide icons
  - `logo:brand-name` for Simple Icons logos
- `size` (number, optional): Icon size in pixels (default: 20)
- `color` (string, optional): Icon color (default: "currentColor")
- `strokeWidth` (number, optional): Stroke width for Lucide icons (default: 2)
- `className` (string, optional): Additional CSS classes

### Lucide Icons

Use the `lucide:` prefix followed by the icon name in kebab-case:

```tsx
<Icon name="lucide:edit-3" />
<Icon name="lucide:heart" />
<Icon name="lucide:user-circle" />
<Icon name="lucide:star" />
```

### Logo Icons (Simple Icons)

Use the `logo:` prefix followed by the brand name:

```tsx
<Icon name="logo:github" />
<Icon name="logo:figma" />
<Icon name="logo:notion" />
<Icon name="logo:react" />
<Icon name="logo:google-cloud" />
```

### Examples

```tsx
// Different sizes
<Icon name="lucide:heart" size={16} />
<Icon name="lucide:heart" size={24} />
<Icon name="lucide:heart" size={32} />

// Custom colors
<Icon name="lucide:star" color="gold" />
<Icon name="logo:github" color="#333" />

// Custom stroke width for Lucide icons
<Icon name="lucide:edit-3" strokeWidth={1.5} />

// With CSS classes
<Icon name="lucide:user" className="hover:opacity-75" />
```

### Fallback Behavior

- If a Lucide icon is not found, it falls back to `HelpCircle`
- If a logo icon is not found, it falls back to `HelpCircle`
- If no prefix is provided, it falls back to `HelpCircle`

## Available Icon Libraries

### Lucide Icons

Visit [lucide.dev](https://lucide.dev) for the complete list of available icons.

### Simple Icons

Visit [simpleicons.org](https://simpleicons.org) for the complete list of available brand logos.