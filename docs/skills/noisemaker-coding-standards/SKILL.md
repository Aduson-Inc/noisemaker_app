# NOiSEMaKER Coding Standards Skill

## Description
Enforces consistent coding standards across the NOiSEMaKER monorepo. Ensures all generated code follows project conventions.

---

## Frontend Standards (Next.js/React/TypeScript)

### File Naming
| Type | Convention | Example |
|------|------------|---------|
| Components | PascalCase | `HeroSection.tsx` |
| Pages (App Router) | lowercase folders | `app/dashboard/page.tsx` |
| Utilities | camelCase | `formatDate.ts` |
| Hooks | camelCase with `use` prefix | `useAuth.ts` |
| Types | PascalCase | `UserProfile.ts` |
| Constants | SCREAMING_SNAKE_CASE | `API_ENDPOINTS.ts` |

### Component Structure
```tsx
// 1. Imports (external first, then internal)
import { useState } from 'react';
import { Button } from '@/components/ui/button';

// 2. Types/Interfaces
interface ComponentProps {
  title: string;
  onAction: () => void;
}

// 3. Component
export function ComponentName({ title, onAction }: ComponentProps) {
  // 3a. Hooks first
  const [state, setState] = useState(false);
  
  // 3b. Handlers
  const handleClick = () => {
    onAction();
  };
  
  // 3c. Render
  return (
    <div className="...">
      {title}
    </div>
  );
}
```

### Tailwind CSS Rules
- Use Tailwind 4.x syntax
- Prefer utility classes over custom CSS
- Group classes logically: layout → spacing → typography → colors → effects
- Use CSS variables for theme colors defined in globals.css
```tsx
// GOOD
<div className="flex items-center gap-4 p-6 text-lg text-white bg-purple-900/80 backdrop-blur-sm">

// BAD - unorganized
<div className="text-white p-6 flex bg-purple-900/80 gap-4 items-center backdrop-blur-sm text-lg">
```

### Import Aliases
Always use the `@/` alias for internal imports:
```tsx
// GOOD
import { Button } from '@/components/ui/button';
import { useAuth } from '@/lib/hooks/useAuth';

// BAD
import { Button } from '../../../components/ui/button';
```

---

## Backend Standards (Python/FastAPI)

### File Naming
| Type | Convention | Example |
|------|------------|---------|
| Modules | snake_case | `user_manager.py` |
| Classes | PascalCase | `class UserManager:` |
| Functions | snake_case | `def get_user_by_id():` |
| Constants | SCREAMING_SNAKE_CASE | `MAX_RETRY_COUNT = 3` |
| Private | leading underscore | `_internal_helper()` |

### Function Structure
```python
def function_name(
    required_param: str,
    optional_param: int = 10,
    *,
    keyword_only: bool = False
) -> ReturnType:
    """
    Brief description of function.
    
    Args:
        required_param: Description of param
        optional_param: Description with default
        keyword_only: Forces keyword argument
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When validation fails
    """
    # Implementation
    pass
```

### DynamoDB Conventions
```python
# Table name references - ALWAYS use noisemaker- prefix
TABLE_USERS = 'noisemaker-users'
TABLE_SONGS = 'noisemaker-songs'

# NEVER use old naming
# BAD: 'spotify-promo-users'
```

### S3 Conventions
```python
# Bucket name - single bucket for all app data
BUCKET_NAME = 'noisemakerpromobydoowopp'

# Paths within bucket
ARTWORK_PATH = 'ArtSellingONLY/'
TEMPLATES_PATH = 'content-colortemplates/'
MILESTONES_PATH = 'Milestones/'
SCHEDULED_PATH = 'scheduled-content/'
USER_ART_PATH = 'UserSpotifyArt/'
```

### Parameter Store Conventions
```python
# ALWAYS use /noisemaker/ prefix
PARAM_JWT_SECRET = '/noisemaker/jwt_secret_key'
PARAM_STRIPE_KEY = '/noisemaker/stripe_secret_key'

# NEVER use old paths
# BAD: '/spotify-promo/jwt-secret-key'
```

---

## API Endpoint Standards

### URL Structure
```
/api/{resource}/{action}
/api/{resource}/{id}
/api/{resource}/{id}/{sub-resource}
```

### Examples
```
GET    /api/user/{user_id}/songs
POST   /api/songs/add-from-url
GET    /api/marketplace/artwork
POST   /api/payment/create-checkout
GET    /api/oauth/{platform}/connect
```

### Response Format
```python
# Success
{
    "success": True,
    "data": { ... },
    "message": "Operation completed"
}

# Error
{
    "success": False,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "User-friendly message"
    }
}
```

---

## Git Commit Standards

### Format
```
<type>: <short description>

<optional body>

<optional footer>
```

### Types
| Type | Use For |
|------|---------|
| feat | New feature |
| fix | Bug fix |
| docs | Documentation only |
| style | Formatting, no code change |
| refactor | Code restructuring |
| test | Adding tests |
| chore | Maintenance tasks |

### Examples
```
feat: Add milestone video player component

fix: Correct S3 bucket path for artwork uploads

docs: Update AWS inventory with verified resources

refactor: Migrate spotify-promo references to noisemaker
```

---

## Prohibited Patterns

### NEVER DO:
- Use `any` type in TypeScript (use `unknown` or proper types)
- Leave console.log in production code
- Hardcode secrets or API keys
- Use `var` in JavaScript/TypeScript (use `const` or `let`)
- Mix tabs and spaces (use 2 spaces for frontend, 4 for backend)
- Create files outside the established folder structure
- Reference old `spotify-promo-*` naming anywhere

### ALWAYS DO:
- Add TypeScript types to all function parameters and returns
- Handle errors with try/catch
- Use environment variables for configuration
- Write self-documenting code with clear variable names
- Follow existing patterns in the codebase
