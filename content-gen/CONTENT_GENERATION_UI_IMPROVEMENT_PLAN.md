# Content Generation UI Improvement Plan

## Overview
This plan aligns the main content generation flow UI with the Figma design, incorporating Coral UI patterns from `coralUIComponents`.

---

## 1. Task Header Banner
**Location**: Top of chat panel  
**Current State**: No task header  
**Target State**: Purple/blue gradient banner showing current task

### Changes Required:
- [ ] Add a `TaskHeader` component that displays above messages
- [ ] Style: Purple/blue gradient background (#5c3d91 to #6366f1)
- [ ] Show task description: "Generate an ad copy and image ideas for a Facebook campaign promoting 'Paint for Home Decor'"
- [ ] Conditionally display based on conversation state

### Files to Modify:
- `ChatPanel.tsx` - Add TaskHeader component integration

---

## 2. Message Bubbles Styling
**Location**: `ChatPanel.tsx` - `MessageBubble` component  
**Current State**: Basic card styling with Fluent UI  
**Target State**: Coral-style message bubbles matching Figma

### Changes Required:
- [ ] **User Messages**: 
  - Background: `var(--colorNeutralBackground2)` (light gray, similar to Coral)
  - Align: Right-aligned, rounded corners (6px)
  - Max-width: 80%
  - Remove avatar for user messages (match Figma simplicity)
  
- [ ] **Assistant Messages**:
  - Background: White/transparent
  - Full width, no avatar circle (match Coral pattern)
  - Clean markdown rendering with proper list styling
  - Footer: "AI generated content may be incorrect" text + thumbs up/down icons

- [ ] **Markdown Rendering Improvements**:
  - Import Coral's markdown styles (bullet points, code blocks)
  - Add proper spacing between paragraphs
  - Style inline code and code blocks

### Files to Modify:
- `ChatPanel.tsx` - Refactor MessageBubble component
- `global.css` - Add Coral markdown styles

---

## 3. Brief Review Card (BriefReview.tsx)
**Current State**: Card with bot avatar and sections  
**Target State**: Cleaner card matching Figma's brief format

### Changes Required:
- [ ] Remove bot avatar (inline with messages)
- [ ] Update card layout to show:
  - Campaign Objective
  - Audience  
  - Create instructions ("Create a square image of a living space...")
  - Tone & Style
  - Deliverables
- [ ] Section styling:
  - Bold section labels (e.g., "Tone & Style:")
  - Clean gray background sections
  - Modern, warm tone indicators
- [ ] Button styling:
  - "Start over" - outline style button
  - "Confirm brief" - filled primary button

### Files to Modify:
- `BriefReview.tsx` - Restructure layout and styling

---

## 4. Product Selection Cards
**Location**: New component or update `ProductReview.tsx`  
**Current State**: Basic product list with images  
**Target State**: Two display modes - List and Grid (like Figma)

### Changes Required:
- [ ] **List View (Style 1)**:
  - Product color circle on left (shows actual paint color)
  - Product name (bold), description, price vertically stacked
  - "Select" button on right (outlined, blue on hover/selected)
  - Hover state: subtle background highlight
  - Click to select/deselect

- [ ] **Grid View (Style 2)**:
  - 2x2 grid layout
  - Color circle, name, description, price in each cell
  - Card-like appearance with subtle borders

- [ ] **View Toggle Links**:
  - "list style 1" / "list style 2" links to switch between views
  - Style as blue links with parentheses styling

- [ ] **Selection State**:
  - Visual indicator when product is selected
  - Support for multi-select or single-select based on context

### Files to Modify:
- `ProductReview.tsx` - Major refactor for dual display modes
- Create `ProductCard.tsx` - Reusable product card component
- Create `ProductGrid.tsx` - Grid layout component

---

## 5. Generated Content Preview (InlineContentPreview.tsx)
**Current State**: Grid layout with images and copy  
**Target State**: Figma-style content display with text overlay images

### Changes Required:
- [ ] **Header Section**:
  - Sparkle emoji with headline: "✨ Discover the serene elegance of Snow Veil (EEEFEA) ✨"
  
- [ ] **Body Copy Section**:
  - Clean paragraph formatting
  - Proper line height and spacing
  - Hashtags in brand blue color at bottom

- [ ] **Image Preview**:
  - Single large image OR side-by-side images
  - Product name overlay on image (top-left, white text with shadow)
  - Subtitle text below product name
  - Clean rounded corners (8px)

- [ ] **Action Chips/Buttons**:
  - "Create an other image with same paint color, but a modern kitchen area, with no text on it"
  - Styled as clickable blue pill/chip

- [ ] **Footer Actions**:
  - Thumbs up/down feedback
  - "AI generated content may be incorrect" disclaimer

### Files to Modify:
- `InlineContentPreview.tsx` - Refactor content layout
- Add request chip/quick action component

---

## 6. Input Box Styling
**Location**: Bottom of `ChatPanel.tsx`  
**Current State**: Simple input with + and send icons  
**Target State**: Coral-style input wrapper with focus animation

### Changes Required:
- [ ] **Container**:
  - White background with subtle border
  - Rounded corners (4px like current, or 8px for more modern)
  - Focus state: animated underline indicator (purple/blue)
  
- [ ] **Input Field**:
  - Auto-expanding textarea (from Coral Chat.tsx pattern)
  - "Type a message" placeholder
  - Transparent background
  
- [ ] **Action Buttons**:
  - Attach/Plus icon on bottom-left area
  - Send icon on bottom-right
  - Vertical divider between attachment and send
  - AI-Generated tag/tooltip

- [ ] **Disclaimer**:
  - "AI generated content may be incorrect. Check for mistakes."
  - Positioned below input OR as tooltip on AI-Generated tag

### Files to Modify:
- `ChatPanel.tsx` - Update input area styling
- `global.css` - Add focus indicator animation

---

## 7. Chat History Panel (ChatHistory.tsx)
**Current State**: Simplified list with "See all" link  
**Target State**: Coral-style history panel

### Changes Required:
- [ ] Ensure consistent styling with Coral's ChatHistory component
- [ ] Loading states with spinner
- [ ] Selection state styling
- [ ] Date formatting (Today, Yesterday, X days ago)

### Files to Modify:
- `ChatHistory.tsx` - Minor alignment tweaks
- `ChatHistory.css` (if needed)

---

## 8. Loading/Typing States
**Current State**: Basic spinner with text  
**Target State**: Coral-style "Thinking..." indicator

### Changes Required:
- [ ] Update loading indicator to match Coral's typing-indicator style
- [ ] Animated dots or subtle pulse animation
- [ ] "Thinking..." text styling

### Files to Modify:
- `ChatPanel.tsx` - Update loading state UI

---

## 9. Global Styles & CSS Variables
**Location**: `global.css`  
**Current State**: Basic Fluent UI integration  
**Target State**: Full Coral CSS patterns

### Changes Required:
- [ ] Import/merge Coral's CSS patterns:
  - Input wrapper styles with focus indicator
  - Message styling (.user, .assistant classes)
  - Custom scrollbar styling
  - Markdown content styling
  - Animation keyframes

### Files to Modify:
- `global.css` - Merge Coral patterns

---

## 10. Component Structure Improvements

### New Components to Create:
1. `TaskHeader.tsx` - Task description banner
2. `ProductCard.tsx` - Reusable product display card
3. `ActionChip.tsx` - Clickable action pill/chip for quick requests
4. `ViewToggle.tsx` - List/Grid view toggle links

### Components to Refactor:
1. `MessageBubble` (in ChatPanel.tsx) - Coral-style messages
2. `BriefReview.tsx` - Cleaner brief display
3. `ProductReview.tsx` - Dual view mode support
4. `InlineContentPreview.tsx` - Better content layout

---

## Implementation Priority

### Phase 1: Core Chat Experience (High Priority)
1. Message bubble styling (user/assistant)
2. Input box with Coral patterns
3. Loading states

### Phase 2: Content Generation Flow (High Priority)
4. Brief review card improvements
5. Product selection cards (list + grid views)
6. Generated content preview

### Phase 3: Polish & Enhancement (Medium Priority)
7. Task header banner
8. Action chips for quick requests
9. Chat history alignment
10. Global CSS cleanup

---

## Dependencies

### From Coral UI (`coralUIComponents/src/frontend/App/`):
- `modules/Chat.css` - Input wrapper, message styles
- `index.css` - Global styles, scrollbar
- `modules/Chat.tsx` - Input pattern reference
- `components/ChatHistory/ChatHistory.css` - History styling

### Fluent UI Components Used:
- Button, Card, Text, Badge, Tooltip, Divider, Spinner
- Icons: Send, Add, ThumbLike, ThumbDislike, Bot, Person

---

## Success Criteria
1. ✅ Message bubbles match Figma styling (user right, assistant left/full-width)
2. ✅ Input box has Coral-style focus animation
3. ✅ Brief review card shows all sections cleanly
4. ✅ Product selection has both list and grid view options
5. ✅ Generated content shows images with text overlays
6. ✅ Action chips allow quick follow-up requests
7. ✅ Consistent spacing, fonts, and colors throughout
8. ✅ Responsive design maintained for all screen sizes
